#!/usr/bin/env python3
"""Landed cost calculator: Korean car price -> price delivered to the client's city.

Usage:
  python3 viral-max/tools/landed_cost.py --price-krw 28000000 --cc 2200 --dest example-country
  python3 viral-max/tools/landed_cost.py --price-krw 28000000 --cc 2200 --dest example-country --mode roro --json

Edit viral-max/tools/destinations.json to add countries and your real costs.
"""
import argparse
import json
from pathlib import Path

CONFIG = Path(__file__).with_name("destinations.json")


def calculate(price_krw, cc, dest, mode="container", config=None):
    cfg = config or json.loads(CONFIG.read_text())
    rate = cfg["krw_per_usd"]
    d = cfg["destinations"][dest]

    car_usd = price_krw / rate
    korea_fees_usd = sum(cfg["korea_side_krw"].values()) / rate
    fob = car_usd + korea_fees_usd

    freight = d["freight_usd"][mode]
    insurance = (fob + freight) * cfg["insurance_rate"]
    cif = fob + freight + insurance

    duty = cif * d["import_duty_rate"] + cc * d["import_duty_per_cc_usd"]
    excise = cc * d["excise_per_cc_usd"]
    vat = (cif + duty + excise) * d["vat_rate"]

    lines = [
        ("Car price in Korea", car_usd),
        ("Korea fees (auction, docs, truck, port)", korea_fees_usd),
        (f"Ocean freight ({mode})", freight),
        ("Insurance", insurance),
        ("Destination port charges", d["destination_port_charges_usd"]),
        ("Import duty", duty),
        ("Excise", excise),
        ("VAT", vat),
        ("Recycling fee", d["recycling_fee_usd"]),
        ("Broker, certification, registration", d["broker_certification_registration_usd"]),
        (f"Delivery to {d['city']}", d["inland_to_city_usd"]),
        ("Service fee", cfg["service_fee_usd"]),
    ]
    return {"fob": fob, "cif": cif, "lines": lines, "total": sum(v for _, v in lines)}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--price-krw", type=float, required=True, help="car price in Korean won")
    p.add_argument("--cc", type=int, default=0, help="engine size in cc (0 for EV)")
    p.add_argument("--dest", required=True, help="key in destinations.json")
    p.add_argument("--mode", choices=["container", "roro"], default="container")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    r = calculate(a.price_krw, a.cc, a.dest, a.mode)
    if a.json:
        print(json.dumps(r, indent=2))
        return
    print("RECEIPT: Korea to your city")
    print("-" * 52)
    for name, value in r["lines"]:
        print(f"{name:<42}${value:>9,.0f}")
    print("-" * 52)
    print(f"{'FOB Korea':<42}${r['fob']:>9,.0f}")
    print(f"{'CIF destination port':<42}${r['cif']:>9,.0f}")
    print(f"{'TOTAL DELIVERED':<42}${r['total']:>9,.0f}")


if __name__ == "__main__":
    main()
