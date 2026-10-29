#!/usr/bin/env python3
"""Car broker calculator: Korean car -> exact delivered price in the client's city, as a Russian PDF quote.

Usage:
  python3 viral-max/tools/landed_cost.py viral-max/quotes/example-request.json
  python3 viral-max/tools/landed_cost.py request.json --no-pdf

Compare several countries at once (and get a ready caption for videos): put a "destinations" list in the
request instead of country/city, e.g. "destinations": [{"country": "kazakhstan", "city": "Алматы"}, ...].

Request JSON: model, year, month (optional), fuel (petrol|diesel|hybrid|plug_in_hybrid|ev|lpg),
engine_cc, power_hp (needed by countries that tax or limit by hp), motor_kw (EV, optional), mileage_km, price_krw, country, city,
shipping (container|roro).

Your own costs: viral-max/tools/costs.json
Country customs rules: viral-max/tools/countries/<country>.json (schema in countries/_template.json)
Writes viral-max/quotes/NNN-<model>-<city>.md and .pdf.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
QUOTES = TOOLS.parent / "quotes"
FUEL_RU = {"petrol": "бензин", "diesel": "дизель", "hybrid": "гибрид", "plug_in_hybrid": "плагин-гибрид",
           "ev": "электро", "lpg": "газ (LPG)"}
GROUPS_RU = {
    "korea": "1. Расходы в Корее",
    "logistics": "2. Логистика: Корея → порт назначения",
    "customs": "3. Таможня и налоги",
    "local": "4. Оформление и доставка до города",
    "service": "5. Услуги компании",
}


BASE_RU = {"car": "цена авто", "fob": "FOB", "freight": "фрахт", "insurance": "страховка", "cif": "CIF"}


CHECK_MARK = {"official": "", "sources": "", "estimate": " ⚠️"}


class QuoteError(Exception):
    pass


def check_of(obj, key="check"):
    """official = official source, sources = 2+ open sources agree, estimate = needs confirmation."""
    if obj.get(key):
        return obj[key]
    return "official" if obj.get("verified") else "estimate"


def money(x):
    return f"{x:,.0f}".replace(",", " ")


def matches(when, car):
    if not when:
        return True
    if "fuel" in when and car["fuel"] not in when["fuel"]:
        return False
    if ("hp_min" in when or "hp_max" in when) and not car.get("power_hp"):
        raise QuoteError("Для расчёта нужна мощность двигателя (power_hp, л.с.)")
    checks = [("age_min", "age_max", car["age"]), ("cc_min", "cc_max", car["engine_cc"]),
              ("price_min_usd", "price_max_usd", car["price_usd"]),
              ("price_min_eur", "price_max_eur", car["price_eur"]),
              ("hp_min", "hp_max", car.get("power_hp") or 0)]
    for lo, hi, v in checks:
        if lo in when and v < when[lo]:
            return False
        if hi in when and v >= when[hi]:
            return False
    return True


def evaluate(item, car, values, fx, currency, labels=BASE_RU):
    """Return (usd_amount, detail_ru) or None if the item doesn't apply to this car."""
    if not matches(item.get("when"), car):
        return None
    cur = item.get("currency", currency)
    if cur not in fx:
        raise QuoteError(f"Нет курса валюты {cur} в costs.json → fx")
    t = item["type"]
    if t == "error":
        raise QuoteError(item["message_ru"])
    if t == "percent":
        base = sum(values[b] for b in item["base"])
        return item["rate"] * base, f"{item['rate'] * 100:g}% от ({' + '.join(labels.get(b, b) for b in item['base'])} = ${money(base)})"
    if t in ("per_cc", "per_hp", "per_kw"):
        key, unit = {"per_cc": ("engine_cc", "см³"), "per_hp": ("power_hp", "л.с."), "per_kw": ("motor_kw", "кВт")}[t]
        if car.get(key) is None:
            raise QuoteError(f"Для расчёта нужен параметр {key}")
        return item["rate"] * car[key] / fx[cur], f"{item['rate']:g} {cur} × {car[key]} {unit}"
    if t == "fixed":
        amount = item["amount"]
        return amount / fx[cur], (f"{money(amount)} {cur}" if cur != "USD" else "фиксированно")
    if t in ("max", "choose"):
        results = []
        for opt in item["options"]:
            r = evaluate(opt, car, values, fx, cur, labels)
            if r is not None:
                if t == "choose":
                    return r
                results.append(r)
        if not results:
            return None
        best = max(results, key=lambda r: r[0])
        return best[0], best[1] + " (наибольшее из вариантов)"
    raise QuoteError(f"Неизвестный тип {t}")


REQUIRED = ["model", "year", "fuel", "price_krw", "country", "city"]


def calculate(req, costs=None, profile=None, today=None):
    missing = [k for k in REQUIRED if req.get(k) in (None, "")]
    if req.get("fuel") != "ev" and not req.get("engine_cc"):
        missing.append("engine_cc")
    if missing:
        raise QuoteError(f"Не хватает данных об автомобиле: {', '.join(missing)}")
    if req["fuel"] not in FUEL_RU:
        raise QuoteError(f"Неизвестный тип топлива {req['fuel']}. Варианты: {', '.join(FUEL_RU)}")
    req = {"engine_cc": 0, **req}
    costs = costs or json.loads((TOOLS / "costs.json").read_text())
    path = TOOLS / "countries" / f"{req['country']}.json"
    if profile is None:
        if not path.exists():
            raise QuoteError(f"Нет профиля страны {path.name}. Создай его по countries/_template.json")
        profile = json.loads(path.read_text())
    fx = costs["fx"]
    today = today or dt.date.today()
    made = dt.date(req["year"], req.get("month", 1), 1)
    price_usd = req["price_krw"] / fx["KRW"]
    car = {**req, "age": (today - made).days / 365.25, "price_usd": price_usd, "price_eur": price_usd * fx["EUR"]}
    if req["city"] not in profile["cities"]:
        raise QuoteError(f"Нет города {req['city']} в профиле. Есть: {', '.join(profile['cities'])}")
    city = profile["cities"][req["city"]]
    mode = req.get("shipping", "container")

    lines = []  # (group, name, usd, detail, check)
    lines.append(("korea", "Цена автомобиля в Корее", price_usd, f"₩{money(req['price_krw'])}", "official"))
    for name, krw in costs["korea_side_krw"].items():
        lines.append(("korea", name, krw / fx["KRW"], f"₩{money(krw)}", check_of(costs, "korea_check")))
    fob = sum(l[2] for l in lines)
    freight = profile["freight_usd"][mode]
    insurance = (fob + freight) * costs["insurance_rate"]
    freight_check = profile.get("freight_check") or ("official" if profile.get("freight_verified") else "estimate")
    lines.append(("logistics", f"Доставка ({'контейнер' if mode == 'container' else 'RoRo'})", freight,
                  profile["route_ru"], freight_check))
    lines.append(("logistics", "Страховка груза", insurance, f"{costs['insurance_rate'] * 100:g}% от FOB + фрахт", "official"))
    cif = fob + freight + insurance
    if profile["port_charges_usd"]:
        lines.append(("logistics", "Портовые сборы и выгрузка", profile["port_charges_usd"], "", freight_check))

    values = {"car": price_usd, "fob": fob, "freight": freight, "insurance": insurance, "cif": cif}
    labels = {**BASE_RU, **{i["id"]: i["name_ru"].lower() for i in profile["items"]}}
    for item in profile["items"]:
        try:
            r = evaluate(item, car, values, fx, profile["currency"], labels)
        except QuoteError as e:
            # e.g. private import not allowed for this age: clear it through the legal-entity alternative instead
            if not profile.get("alternative") or req.get("_no_alt"):
                raise
            alt = profile["alternative"]
            q = calculate({**req, "country": alt["profile"], "_no_alt": True}, costs, None, today)
            q["fallback"] = (str(e), alt["name_ru"])
            return q
        values[item["id"]] = r[0] if r else 0
        if r:
            lines.append((item["group"], item["name_ru"], r[0], r[1], check_of(item)))
    if city["inland_usd"]:
        lines.append(("local", f"Доставка до города {req['city']}", city["inland_usd"], city.get("days_ru", ""),
                      check_of(city)))
    lines.append(("service", "Услуги компании (подбор, проверка, выкуп, сопровождение)", costs["service_fee_usd"], "",
                  check_of(costs, "service_check")))

    total = sum(l[2] for l in lines)
    alt = None
    if profile.get("alternative") and not req.get("_no_alt"):
        a = profile["alternative"]
        try:
            aq = calculate({**req, "country": a["profile"], "_no_alt": True}, costs, None, today)
        except QuoteError as e:
            alt = (a["name_ru"], str(e))
        else:
            if aq["total"] < total:
                # a broker would pick the cheaper legal route, so quote that one and show ours for comparison
                aq["fallback"] = ("через юрлицо дешевле", a["name_ru"])
                aq["alt"] = (f"ввоз на физлицо ({profile['country_ru']}, ЕТС)", total)
                return aq
            alt = (a["name_ru"], aq["total"])
    return {"car": car, "profile": profile, "costs": costs, "lines": lines, "fob": fob, "cif": cif,
            "total": total, "today": today, "alt": alt}


def car_table(c):
    return ["## Автомобиль", "", "| Параметр | Значение |", "|---|---|",
            f"| Модель | {c['model']} |",
            f"| Год выпуска | {c['year']}{'/' + str(c['month']).zfill(2) if c.get('month') else ''} (возраст {c['age']:.1f} г.) |",
            f"| Топливо | {FUEL_RU.get(c['fuel'], c['fuel'])} |",
            f"| Объём двигателя | {c.get('engine_cc') or '—'} см³ |",
            f"| Мощность | {c.get('power_hp') or '—'} л.с. |",
            f"| Пробег | {money(c['mileage_km'])} км |" if c.get("mileage_km") else "| Пробег | — |",
            f"| Цена в Корее | ₩{money(c['price_krw'])} (${money(c['price_usd'])}) |", ""]


def local_total(q):
    p, fx = q["profile"], q["costs"]["fx"]
    cur = p["currency"]
    if cur == "USD" or cur not in fx:
        return None
    return f"{money(q['total'] * fx[cur])} {p.get('currency_symbol', cur)}"


def render_ru(q, standalone=True):
    c, p, costs = q["car"], q["profile"], q["costs"]
    fx = costs["fx"]
    valid = q["today"] + dt.timedelta(days=costs.get("quote_valid_days", 7))
    estimates = [l for l in q["lines"] if l[4] == "estimate"]
    sourced = [l for l in q["lines"] if l[4] == "sources"]
    if standalone:
        out = [f"# Расчёт стоимости: {c['model']} → {c['city']}", "",
               f"**Дата расчёта:** {q['today']:%d.%m.%Y} · **Действителен до:** {valid:%d.%m.%Y} · "
               f"**Страна:** {p['country_ru']}", ""] + car_table(c)
    else:
        out = []
    for group, title in GROUPS_RU.items():
        rows = [l for l in q["lines"] if l[0] == group]
        if not rows:
            continue
        out += [f"## {title}", "", "| № | Статья | Как считается | Сумма, $ |", "|---|---|---|---|"]
        for i, (_, name, usd, detail, chk) in enumerate(rows, 1):
            out.append(f"| {i} | {name}{CHECK_MARK[chk]} | {detail} | {money(usd)} |")
        out += [f"| | **Итого по разделу** | | **{money(sum(r[2] for r in rows))}** |", ""]
    out += ["## ИТОГО", "", "| | Сумма |", "|---|---|",
            f"| Цена FOB Корея | ${money(q['fob'])} |",
            f"| Цена CIF порт назначения | ${money(q['cif'])} |",
            f"| **ИТОГО с доставкой в {c['city']}** | **${money(q['total'])}** |"]
    if local_total(q):
        out.append(f"| **В местной валюте** | **{local_total(q)}** |")
    out += [f"| В вонах | ₩{money(q['total'] * fx['KRW'])} |"]
    if q.get("fallback"):
        out.append(f"| Способ растаможки | {q['fallback'][1]}: {q['fallback'][0][0].lower() + q['fallback'][0][1:]} |")
    if q.get("alt"):
        name, val = q["alt"]
        out.append(f"| Для сравнения: {name} | {'$' + money(val) if isinstance(val, float) else val} |")
    out += [""]
    out += ["## Сроки", "", f"- Маршрут: {p['route_ru']}", f"- Доставка из Кореи: {p['transit_days_ru']}",
            f"- Доставка до города: {p['cities'][c['city']].get('days_ru', '—')}", ""]
    if p.get("documents_ru"):
        out += ["## Документы", ""] + [f"- {d}" for d in p["documents_ru"]] + [""]
    if p.get("restrictions_ru"):
        out += ["## Ограничения и важно знать", ""] + [f"- {r}" for r in p["restrictions_ru"]] + [""]
    out += ["## Точность расчёта", ""]
    if estimates:
        out += ["> ⚠️ **Оценка, требует подтверждения:** " + ", ".join(l[1] for l in estimates) +
                ". Уточняется у перевозчика или брокера перед оплатой.", ""]
    if sourced:
        out += ["- По данным нескольких открытых источников (калькуляторы, СМИ): " + ", ".join(l[1] for l in sourced) + ".", ""]
    if not estimates and not sourced:
        out += ["> ✅ Все статьи подтверждены по официальным источникам.", ""]
    fx_list = ", ".join(f"1 USD = {money(v) if v >= 100 else f'{v:g}'} {k}" for k, v in fx.items() if k != "USD")
    if not standalone:
        out = [l.replace("## ", "### ", 1) if l.startswith("## ") else l for l in out]
    out += [f"- Курсы валют на {costs.get('fx_date', '—')}: {fx_list}",
            f"- Правила страны проверены: {p.get('verified_on', '—')}",
            "- Окончательная сумма таможенных платежей определяется таможней страны назначения в день оформления.", ""]
    if p.get("sources"):
        out += ["**Источники:**", ""] + [f"- {s}" for s in p["sources"]] + [""]
    return "\n".join(out)


def compare(req):
    """Run the quote for every destination; failures become a reason instead of stopping the rest."""
    results = []
    for d in req["destinations"]:
        r = {k: v for k, v in req.items() if k != "destinations"}
        r.update(d)
        try:
            results.append((d, calculate(r), None))
        except QuoteError as e:
            results.append((d, None, str(e)))
    return results


def caption_ru(results, today):
    lines = [f"💰 Цена под ключ из Кореи (расчёт на {today:%d.%m.%Y}):"]
    for d, q, err in results:
        flag = ""
        path = TOOLS / "countries" / f"{d['country']}.json"
        if path.exists():
            flag = json.loads(path.read_text()).get("flag", "")
        if err:
            lines.append(f"{flag} {d['city']}: ❌ {err.split(':')[0].lower()}")
            continue
        approx = "≈ " if any(l[4] == "estimate" for l in q["lines"]) else ""
        loc = local_total(q)
        lines.append(f"{flag} {d['city']}: {approx}${money(q['total'])}" + (f" ({loc})" if loc else "")
                     + (" — через юрлицо" if q.get("fallback") else ""))
    lines.append("Точный расчёт под твою машину — пиши в директ 📩")
    return lines


def render_compare_ru(req, results):
    ok = [(d, q) for d, q, e in results if q]
    if not ok:
        raise QuoteError("Ни одна страна не рассчитана: " + "; ".join(e for _, _, e in results))
    today, c = ok[0][1]["today"], ok[0][1]["car"]
    out = [f"# Сравнение: {req['model']} — {len(results)} страны", "",
           f"**Дата расчёта:** {today:%d.%m.%Y}", ""] + car_table(c)
    out += ["## Итог по странам", "", "| Страна | Город | Итого, $ | В местной валюте | Точность |", "|---|---|---|---|---|"]
    for d, q, err in results:
        if err:
            out.append(f"| {d['country']} | {d['city']} | — | — | ❌ {err} |")
        else:
            n_est = sum(1 for l in q["lines"] if l[4] == "estimate")
            out.append(f"| {q['profile']['country_ru']} | {d['city']} | **{money(q['total'])}** | {local_total(q) or '—'} | "
                       f"{'⚠️ оценок: ' + str(n_est) if n_est else '✅'} |")
    out += ["", "## Готовый текст для описания видео", "", "```"] + caption_ru(results, today) + ["```", ""]
    for d, q in ok:
        out += [f"## {q['profile']['country_ru']}, {d['city']}", ""] + render_ru(q, standalone=False).split("\n")
    return "\n".join(out)


def next_path(model, city):
    QUOTES.mkdir(exist_ok=True)
    nums = [int(m.group(1)) for f in QUOTES.glob("*.md") if (m := re.match(r"(\d{3})-", f.name))]
    slug = re.sub(r"[^\w]+", "-", f"{model}-{city}".lower()).strip("-")[:60]
    return QUOTES / f"{max(nums, default=0) + 1:03d}-{slug}.md"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("request", help="request JSON file")
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    req = json.loads(Path(a.request).read_text())
    try:
        if "destinations" in req:
            results = compare(req)
            text = render_compare_ru(req, results)
            md = next_path(req["model"], "сравнение")
            today = next(q["today"] for _, q, _ in results if q)
            print("\n".join(caption_ru(results, today)))
        else:
            q = calculate(req)
            text = render_ru(q)
            md = next_path(req["model"], req["city"])
            for g, name, usd, _, chk in q["lines"]:
                print(f"{'⚠ ' if chk == 'estimate' else ''}{name:<55}${money(usd):>9}")
            print(f"{'ИТОГО':<55}${money(q['total']):>9}")
    except QuoteError as e:
        sys.exit(f"ОШИБКА: {e}")
    md.write_text(text)
    print(md)
    if not a.no_pdf:
        subprocess.run([sys.executable, str(TOOLS / "make_pdf.py"), str(md)], check=True)


if __name__ == "__main__":
    main()
