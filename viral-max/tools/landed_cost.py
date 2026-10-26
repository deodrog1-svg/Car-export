#!/usr/bin/env python3
"""Car broker calculator: Korean car -> exact delivered price in the client's city, as a Russian PDF quote.

Usage:
  python3 viral-max/tools/landed_cost.py viral-max/quotes/example-request.json
  python3 viral-max/tools/landed_cost.py request.json --no-pdf

Request JSON: model, year, month (optional), fuel (petrol|diesel|hybrid|plug_in_hybrid|ev|lpg),
engine_cc, power_hp (optional), motor_kw (EV, optional), mileage_km, price_krw, country, city,
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


class QuoteError(Exception):
    pass


def money(x):
    return f"{x:,.0f}".replace(",", " ")


def matches(when, car):
    if not when:
        return True
    if "fuel" in when and car["fuel"] not in when["fuel"]:
        return False
    checks = [("age_min", "age_max", car["age"]), ("cc_min", "cc_max", car["engine_cc"]),
              ("price_min_usd", "price_max_usd", car["price_usd"])]
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
    car = {**req, "age": (today - made).days / 365.25, "price_usd": price_usd}
    if req["city"] not in profile["cities"]:
        raise QuoteError(f"Нет города {req['city']} в профиле. Есть: {', '.join(profile['cities'])}")
    city = profile["cities"][req["city"]]
    mode = req.get("shipping", "container")

    lines = []  # (group, name, usd, detail, verified)
    lines.append(("korea", "Цена автомобиля в Корее", price_usd, f"₩{money(req['price_krw'])}", True))
    for name, krw in costs["korea_side_krw"].items():
        lines.append(("korea", name, krw / fx["KRW"], f"₩{money(krw)}", True))
    fob = sum(l[2] for l in lines)
    freight = profile["freight_usd"][mode]
    insurance = (fob + freight) * costs["insurance_rate"]
    lines.append(("logistics", f"Морской фрахт ({'контейнер' if mode == 'container' else 'RoRo'})", freight,
                  profile["route_ru"], profile.get("freight_verified", False)))
    lines.append(("logistics", "Страховка груза", insurance, f"{costs['insurance_rate'] * 100:g}% от FOB + фрахт", True))
    cif = fob + freight + insurance
    lines.append(("logistics", "Портовые сборы и выгрузка", profile["port_charges_usd"], "", profile.get("freight_verified", False)))

    values = {"car": price_usd, "fob": fob, "freight": freight, "insurance": insurance, "cif": cif}
    labels = {**BASE_RU, **{i["id"]: i["name_ru"].lower() for i in profile["items"]}}
    for item in profile["items"]:
        r = evaluate(item, car, values, fx, profile["currency"], labels)
        values[item["id"]] = r[0] if r else 0
        if r:
            lines.append((item["group"], item["name_ru"], r[0], r[1], item.get("verified", False)))
    lines.append(("local", f"Доставка до города {req['city']}", city["inland_usd"], city.get("days_ru", ""),
                  city.get("verified", False)))
    lines.append(("service", "Услуги компании (подбор, проверка, выкуп, сопровождение)", costs["service_fee_usd"], "", True))

    total = sum(l[2] for l in lines)
    return {"car": car, "profile": profile, "costs": costs, "lines": lines, "fob": fob, "cif": cif,
            "total": total, "today": today}


def render_ru(q):
    c, p, costs = q["car"], q["profile"], q["costs"]
    fx, cur = costs["fx"], p["currency"]
    valid = q["today"] + dt.timedelta(days=costs.get("quote_valid_days", 7))
    unverified = [l for l in q["lines"] if not l[4]]
    out = [f"# Расчёт стоимости: {c['model']} → {c['city']}", "",
           f"**Дата расчёта:** {q['today']:%d.%m.%Y} · **Действителен до:** {valid:%d.%m.%Y} · "
           f"**Страна:** {p['country_ru']}", ""]
    out += ["## Автомобиль", "", "| Параметр | Значение |", "|---|---|",
            f"| Модель | {c['model']} |",
            f"| Год выпуска | {c['year']}{'/' + str(c['month']).zfill(2) if c.get('month') else ''} (возраст {c['age']:.1f} г.) |",
            f"| Топливо | {FUEL_RU.get(c['fuel'], c['fuel'])} |",
            f"| Объём двигателя | {c.get('engine_cc') or '—'} см³ |",
            f"| Мощность | {c.get('power_hp') or '—'} л.с. |",
            f"| Пробег | {money(c['mileage_km'])} км |" if c.get("mileage_km") else "| Пробег | — |",
            f"| Цена в Корее | ₩{money(c['price_krw'])} (${money(c['price_usd'])}) |", ""]
    for group, title in GROUPS_RU.items():
        rows = [l for l in q["lines"] if l[0] == group]
        if not rows:
            continue
        out += [f"## {title}", "", "| № | Статья | Как считается | Сумма, $ |", "|---|---|---|---|"]
        for i, (_, name, usd, detail, ok) in enumerate(rows, 1):
            out.append(f"| {i} | {name}{'' if ok else ' ⚠️'} | {detail} | {money(usd)} |")
        out += [f"| | **Итого по разделу** | | **{money(sum(r[2] for r in rows))}** |", ""]
    out += ["## ИТОГО", "", "| | Сумма |", "|---|---|",
            f"| Цена FOB Корея | ${money(q['fob'])} |",
            f"| Цена CIF порт назначения | ${money(q['cif'])} |",
            f"| **ИТОГО с доставкой в {c['city']}** | **${money(q['total'])}** |"]
    if cur != "USD" and cur in fx:
        out.append(f"| **В местной валюте** | **{money(q['total'] * fx[cur])} {cur}** |")
    out += [f"| В вонах | ₩{money(q['total'] * fx['KRW'])} |", ""]
    out += ["## Сроки", "", f"- Маршрут: {p['route_ru']}", f"- Морская доставка: {p['transit_days_ru']}",
            f"- Доставка до города: {p['cities'][c['city']].get('days_ru', '—')}", ""]
    if p.get("documents_ru"):
        out += ["## Документы", ""] + [f"- {d}" for d in p["documents_ru"]] + [""]
    if p.get("restrictions_ru"):
        out += ["## Ограничения и важно знать", ""] + [f"- {r}" for r in p["restrictions_ru"]] + [""]
    out += ["## Точность расчёта", ""]
    if unverified:
        out += ["> ⚠️ **Требует подтверждения:** " + ", ".join(l[1] for l in unverified) +
                ". Эти суммы взяты из открытых источников или оценки и должны быть подтверждены перед оплатой.", ""]
    else:
        out += ["> ✅ Все статьи подтверждены по официальным источникам.", ""]
    fx_list = ", ".join(f"1 USD = {money(v) if v >= 100 else f'{v:g}'} {k}" for k, v in fx.items() if k != "USD")
    out += [f"- Курсы валют на {costs.get('fx_date', '—')}: {fx_list}",
            f"- Правила страны проверены: {p.get('verified_on', '—')}",
            "- Окончательная сумма таможенных платежей определяется таможней страны назначения в день оформления.", ""]
    if p.get("sources"):
        out += ["**Источники:**", ""] + [f"- {s}" for s in p["sources"]] + [""]
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
        q = calculate(req)
    except QuoteError as e:
        sys.exit(f"ОШИБКА: {e}")
    md = next_path(req["model"], req["city"])
    md.write_text(render_ru(q))
    for g, name, usd, _, ok in q["lines"]:
        print(f"{'' if ok else '⚠ '}{name:<55}${money(usd):>9}")
    print(f"{'ИТОГО':<55}${money(q['total']):>9}")
    print(md)
    if not a.no_pdf:
        subprocess.run([sys.executable, str(TOOLS / "make_pdf.py"), str(md)], check=True)


if __name__ == "__main__":
    main()
