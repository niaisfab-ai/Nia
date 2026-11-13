"""Модел: приложение за управление на абонаменти с функция „при смърт“.

Пуска се с:  python3 analysis/abonamenti/model.py
Вход:  analysis/abonamenti/params.csv (всеки параметър с тип и източник)
Изход: analysis/abonamenti/output/*.csv
Всички суми са в USD: източниците са в USD, а курс с източник няма. Не се превалутира.
"""
import csv
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)
SCEN = ["pess", "base", "opt"]
SCEN_BG = {"pess": "песимистичен", "base": "базов", "opt": "оптимистичен"}


def load():
    p = {s: {} for s in SCEN}
    with open(os.path.join(HERE, "params.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for s in SCEN:
                p[s][row["param"]] = float(row[s])
    return p


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# ---------- 1. Пазар ----------
def market(p):
    rows = []
    for s in SCEN:
        q = p[s]
        deaths = q["deaths_us"] + q["deaths_ew"] + q["deaths_eu"]
        cases = deaths * q["share_pay_death"]
        rows.append([SCEN_BG[s], round(deaths), round(cases), round(cases * q["price_death_case"])])
    write("market_bottom_up.csv", ["сценарий", "починали САЩ+А и У+ЕС", "платени случаи", "USD годишно"], rows)
    # Отгоре надолу (research/01, 06, 08): лидерите в категорията и пазарни доклади за дигитално наследство.
    rocket = 351e6      # Rocket Companies, Subscription revenue 2025 (10-K; консолидирано, не изрично Rocket Money)
    monarch = 100e6     # Monarch ARR септ. 2026 (по оценка на Sacra — мнение)
    legacy = [12.65e9, 12.93e9, 16.27e9, 21.86e9, 25e9, 26.019e9]  # 6 платени доклада, 2024–2025, широки дефиниции
    write("market_top_down.csv", ["показател", "USD"], [
        ["Rocket Money приходи от абонаменти 2025", rocket],
        ["Monarch ARR 09.2026 (Sacra)", monarch],
        ["Двата лидера заедно (различни периоди)", rocket + monarch],
        ["Дигитално наследство, мин. от 6 доклада", min(legacy)],
        ["Дигитално наследство, медиана на 6 доклада", statistics.median(legacy)],
        ["Дигитално наследство, макс. от 6 доклада", max(legacy)],
        ["Медианата на докладите / базов отдолу нагоре (пъти)", round(statistics.median(legacy) / rows[1][3])]])
    return rows


# ---------- 2. Икономика на единица (жив потребител, месечен абонамент) ----------
def unit(q):
    net = q["price_month"] * (1 - q["store_fee"])
    agg = q["accounts_per_user"] * q["agg_cost_per_account"]
    cancel = q["cancels_per_user_year"] / 12 * q["cost_per_cancel"]
    contrib = net - agg - q["cloud_per_user"] - cancel
    cac = q["cpi"] / q["conv_install_paid"]
    surv = 1 - q["churn_month"]
    months = lambda n: sum(surv ** t for t in range(n))   # очаквани платени месеци за n месеца
    ltv12, ltv24 = contrib * months(12), contrib * months(24)
    fixed = q["fixed_known"] + q["fixed_other"]
    return dict(net=net, agg=agg, cancel=cancel, contrib=contrib, cac=cac, ltv12=ltv12, ltv24=ltv24,
                profit24=ltv24 - cac, fixed=fixed, m12=months(12), m24=months(24))


def simulate(q, u, months=36):
    """Нови платени клиенти = маркетинг / CAC; всяка кохорта отпада с месечния churn."""
    n_new = q["marketing"] / u["cac"]
    surv = 1 - q["churn_month"]
    active, cash, path = 0.0, 0.0, [0.0]
    for _ in range(months):
        active = active * surv + n_new
        cash += active * u["contrib"] - q["marketing"] - u["fixed"]
        path.append(cash)
    return path, n_new, active


def thresholds(q, u):
    cac_zero = u["ltv24"]
    cac_ss = q["marketing"] * u["ltv24"] / (q["marketing"] + u["fixed"])
    lo, hi = 0.01, max(cac_zero, 0.02)
    for _ in range(60):
        mid = (lo + hi) / 2
        ok = simulate(q, dict(u, cac=mid))[0][-1] >= 0
        lo, hi = (mid, hi) if ok else (lo, mid)
    return cac_zero, cac_ss, lo


def sensitivity(p):
    base = p["base"]
    b = unit(base)["profit24"]
    rows = []
    for key, lab in [("price_month", "Цена на месец"), ("churn_month", "Месечен отлив"), ("conv_install_paid", "Конверсия инсталация → платен"),
                     ("cpi", "Цена на инсталация"), ("cloud_per_user", "Облак на потребител"), ("cost_per_cancel", "Цена на прекратяване")]:
        lo, hi = dict(base), dict(base)
        lo[key] *= 0.8
        hi[key] *= 1.2
        rows.append([lab, round(unit(lo)["profit24"] - b, 2), round(unit(hi)["profit24"] - b, 2)])
    rows.sort(key=lambda r: -max(abs(r[1]), abs(r[2])))
    write("sensitivity.csv", ["допускане", "−20%: промяна USD", "+20%: промяна USD"], rows)
    return b, rows


# ---------- 3. Хипотетичен стартъп (всички данни на стартъпа са ХИПОТЕТИЧНИ, в EUR) ----------
HYPO = dict(arr=120_000, subs=2_000, ebitda=-60_000, ask=50_000, stake=0.05)  # ОЦЕНКА / хипотетично
# Множителите са отношения (без валута), затова се прилагат към EUR. Research/08.
COMPS = {"Credit Karma 2020 (EV/приходи)": 7.1, "Damodaran Software EV/Sales 01.2026": 11.41, "Truebill 2021 (EV/ARR)": 12.75}
GROWTH = [1.00, 0.60, 0.40, 0.30, 0.20]          # ОЦЕНКА
MARGIN = [-0.50, -0.20, 0.00, 0.15, 0.25]        # ОЦЕНКА
TERMINAL_EV_SALES = 11.41                         # Damodaran Software, 01.2026 (research/08)


def dcf(rate):
    rev, pv = HYPO["arr"], 0.0
    for y, (g, m) in enumerate(zip(GROWTH, MARGIN), start=1):
        rev *= 1 + g
        pv += rev * m / (1 + rate) ** y            # ОЦЕНКА: свободен паричен поток ≈ EBITDA
    return pv + rev * TERMINAL_EV_SALES / (1 + rate) ** 5, rev


def valuation():
    m = sorted(COMPS.values())
    comps = [x * HYPO["arr"] for x in m]
    d = {r: dcf(r)[0] for r in (0.50, 0.60, 0.70)}
    eu_seed = (5.0e6, 7.7e6)                       # Европа: pre-seed/seed медиана €5.0 млн.; fintech €7.7 млн. (PitchBook Q3 2025, research/08)
    rows = [["Сравними сделки и множители (EV/ARR)", round(comps[0]), round(comps[1]), round(comps[2])],
            ["Дисконтирани парични потоци (70/60/50%)", round(d[0.70]), round(d[0.60]), round(d[0.50])]]
    lows, mids, highs = [r[1] for r in rows], [r[2] for r in rows], [r[3] for r in rows]
    pre = HYPO["ask"] / HYPO["stake"] - HYPO["ask"]
    rows.append(["ОБЩО (мин / средно на средите / макс)", min(lows), round(sum(mids) / len(mids)), max(highs)])
    rows.append(["Искана pre-money", round(pre), "", ""])
    rows.append(["За сравнение: медиана pre-seed/seed Европа / fintech", eu_seed[0], "", eu_seed[1]])
    rows.append(["Искана pre-money / ARR (пъти)", round(pre / HYPO["arr"], 2), "", ""])
    rows.append(["Дял за 50 000 € при pre-money = ниската по сравними (%)", round(100 * HYPO["ask"] / (comps[0] + HYPO["ask"]), 2), "", ""])
    write("valuation.csv", ["метод", "ниска EUR", "средна EUR", "висока EUR"], rows)
    return rows, pre


def main():
    p = load()
    market(p)
    U = {s: unit(p[s]) for s in SCEN}
    sims = {s: simulate(p[s], U[s]) for s in SCEN}
    rows = []
    for k, lab in [("contrib", "принос на платен потребител на месец USD"), ("cac", "CAC USD"), ("m12", "очаквани платени месеци за 12 мес."),
                   ("m24", "очаквани платени месеци за 24 мес."), ("ltv12", "стойност на клиента 12 мес. USD"), ("ltv24", "стойност на клиента 24 мес. USD"),
                   ("profit24", "печалба от клиент 24 мес. USD"), ("fixed", "постоянни разходи USD/мес.")]:
        rows.append([lab] + [round(U[s][k], 2) for s in SCEN])
    rows.append(["нови платени клиенти/мес. при маркетинг 2 000 USD"] + [round(sims[s][1], 1) for s in SCEN])
    rows.append(["платени клиенти след 36 мес."] + [round(sims[s][2]) for s in SCEN])
    rows.append(["натрупан поток след 36 мес. USD"] + [round(sims[s][0][-1]) for s in SCEN])
    rows.append(["най-ниска точка на натрупания поток (нужен капитал) USD"] + [round(-min(sims[s][0])) for s in SCEN])
    rows.append(["месец, в който натрупаният поток става ≥ 0"] + [next((i for i, v in enumerate(sims[s][0]) if i > 0 and v >= 0 and min(sims[s][0][:i + 1]) < 0), "няма за 36 мес." if sims[s][0][-1] < 0 else "от началото") for s in SCEN])
    write("unit_economics.csv", ["показател"] + [SCEN_BG[s] for s in SCEN], rows)
    write("cashflow_36m.csv", ["месец"] + [SCEN_BG[s] for s in SCEN], [[i] + [round(sims[s][0][i]) for s in SCEN] for i in range(37)])

    q, ub = p["base"], U["base"]
    cz, css, c36 = thresholds(q, ub)
    write("thresholds.csv", ["праг", "стойност"], [
        ["CAC за печалба 0 на клиент (LTV24 = CAC) USD", round(cz, 2)],
        ["CAC, при който стабилният резултат покрива постоянните разходи USD", round(css, 2)],
        ["CAC, при който парите се връщат до 36-ия месец USD", round(c36, 2)],
        ["нужни нови платени клиенти/мес. при CAC за покриване на постоянните разходи (нагоре)", -(-q["marketing"] // css)]])
    budget = 600  # ОЦЕНКА, USD
    installs = budget / q["cpi"]
    need = -(-budget // css)
    write("test_2w.csv", ["показател", "стойност"], [
        ["бюджет USD (ОЦЕНКА)", budget], ["очаквани инсталации при CPI базов", round(installs)],
        ["праг: CAC за покриване на постоянните разходи USD", round(css, 2)],
        ["нужни платени абонати (закръглено нагоре)", int(need)],
        ["нужна конверсия инсталация → платен", round(need / installs, 4)],
        ["базова конверсия (RevenueCat hard paywall)", q["conv_install_paid"]]])
    sensitivity(p)
    valuation()
    print("готово:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
