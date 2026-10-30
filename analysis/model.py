"""Модел: пазарен размер, икономика на единица, сценарии, чувствителност, оценка на хипотетичен стартъп.

Пуска се с:  python3 analysis/model.py
Вход:  analysis/params.csv (всеки параметър с източник или маркер ОЦЕНКА)
Изход: analysis/output/*.csv и reports/figures/*.png
Не чете и не пише в data/.
"""
import csv
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analysis", "output")
FIG = os.path.join(ROOT, "reports", "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

SCEN = ["pess", "base", "opt"]
SCEN_BG = {"pess": "песимистичен", "base": "базов", "opt": "оптимистичен"}
BLUE, ORANGE, GRAY, LIGHT, INK = "#2a78d6", "#eb6834", "#8a8984", "#d6d5d0", "#0b0b0b"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": GRAY, "axes.labelcolor": INK,
    "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.grid": True,
    "grid.color": "#ecebe7", "grid.linewidth": 0.8, "figure.dpi": 150,
})


def load_params():
    p = {s: {} for s in SCEN}
    with open(os.path.join(ROOT, "analysis", "params.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for s in SCEN:
                p[s][row["param"]] = float(row[s])
    return p


def write_csv(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# ---------- 1. Пазарен размер ----------
def market(p):
    bu = {}
    for s in SCEN:
        q = p[s]
        buyers = q["pop_eu"] * q["share_sport_weekly"] * q["share_online_clothes"] * q["share_pay_premium"]
        bu[s] = {"buyers": buyers, "value_eur": buyers * q["orders_12m"] * q["price_gross_market"]}

    # Отгоре надолу: глобален sustainable activewear × дял на Европа в глобалния пазар на спортни облекла.
    # Източници: research/01_razmer_pazar.md
    sust = [5.82, 7.4, 10.2, 14.8]  # млрд. USD, 4 платени доклада
    global_sportswear = 430.3  # млрд. USD, GlobalData 2024
    europe = [20.62, 58.59, 89.88]  # млрд. USD, 3 платени доклада 2024
    shares = [e / global_sportswear for e in europe]
    td = {
        "pess": min(sust) * min(shares),
        "base": statistics.median(sust) * statistics.median(shares),
        "opt": max(sust) * max(shares),
    }
    rows = []
    for s in SCEN:
        rows.append([SCEN_BG[s], round(bu[s]["buyers"]), round(bu[s]["value_eur"] / 1e6, 1), round(td[s], 3)])
    write_csv("market_size.csv", ["сценарий", "купувачи_отдолу_нагоре", "отдолу_нагоре_млн_EUR", "отгоре_надолу_млрд_USD"], rows)
    return bu, td, shares, sust


# ---------- 2. Икономика на единица ----------
def unit(q):
    net = q["price_gross"] / (1 + q["vat"])
    margin = net * q["gross_margin"]
    kept = margin * (1 - q["return_rate"])
    pay = q["price_gross"] * q["pay_pct"] + q["pay_fix"]
    ship = q["ship_cost"]
    ret_ship = q["return_rate"] * q["ship_cost"]
    contrib = kept - pay - ship - ret_ship
    cac = q["cpm"] / (1000 * q["ctr"] * q["cvr"])
    ltv12 = contrib * q["orders_12m"]
    ltv24 = contrib * q["orders_24m"]
    fixed = q["fixed_known"] + q["fixed_other"]
    profit24 = ltv24 - cac
    be_customers = fixed / profit24 if profit24 > 0 else float("inf")
    cogs_unit = net * (1 - q["gross_margin"])
    inventory = q["styles"] * q["moq"] * cogs_unit
    return dict(net=net, margin=margin, kept=kept, pay=pay, ship=ship, ret_ship=ret_ship, contrib=contrib,
                cac=cac, ltv12=ltv12, ltv24=ltv24, fixed=fixed, profit24=profit24,
                be_customers=be_customers, cogs_unit=cogs_unit, inventory=inventory,
                max_cac=ltv24)


def simulate(q, u, months=36):
    """Месечна симулация: нови клиенти = маркетинг / CAC; повторните поръчки на всяка кохорта
    се разпределят равномерно в следващите 23 месеца. Първоначалната стока е паричен разход в месец 0."""
    n_new = q["marketing"] / u["cac"]
    rep_per_month = (q["orders_24m"] - 1) / 23
    cash = -u["inventory"]
    path, monthly = [cash], []
    for t in range(1, months + 1):
        active_cohorts = min(t - 1, 23)
        orders = n_new + n_new * rep_per_month * active_cohorts
        prof = orders * u["contrib"] - q["marketing"] - u["fixed"]
        cash += prof
        path.append(cash)
        monthly.append(prof)
    be_month = next((i + 1 for i, m in enumerate(monthly) if m > 0), None)
    return path, monthly, be_month, n_new


# ---------- 3. Чувствителност ----------
SENS = [("price_gross", "Цена"), ("gross_margin", "Брутен марж"), ("cvr", "Конверсия (→ CAC)"),
        ("orders_24m", "Поръчки за 24 мес."), ("return_rate", "Връщания"), ("ship_cost", "Доставка")]


def sensitivity(p):
    base = p["base"]
    b = unit(base)["profit24"]
    rows = []
    for key, label in SENS:
        lo, hi = dict(base), dict(base)
        lo[key] *= 0.8
        hi[key] *= 1.2
        rows.append((label, unit(lo)["profit24"] - b, unit(hi)["profit24"] - b))
    rows.sort(key=lambda r: -max(abs(r[1]), abs(r[2])))
    write_csv("sensitivity.csv", ["допускане", "−20%: промяна печалба/клиент 24м €", "+20%: промяна €"],
              [[r[0], round(r[1], 2), round(r[2], 2)] for r in rows])
    return b, rows


# ---------- 4. Оценка на хипотетичен стартъп ----------
# ВСИЧКИ входни данни за стартъпа са ХИПОТЕТИЧНИ (потребителят няма данни).
HYPO = dict(revenue=150_000, ebitda=-30_000, customers=1_800, ask=50_000, stake=0.08)
DEALS = {"Allbirds 2026": 0.26, "Icebreaker 2018": 1.13, "Vuori 2024": 5.5, "Allbirds IPO 2021": 9.9}  # Gymshark изключен: множителят смесва USD и GBP
EV_EBITDA = 10.30  # Damodaran US Apparel, 01.2026
EBITDA_MARGIN_Y5 = 0.1147  # Damodaran US Apparel медиана
GROWTH = [0.60, 0.40, 0.30, 0.20, 0.15]  # ОЦЕНКА
MARGINS = [-0.20, -0.05, 0.05, 0.10, EBITDA_MARGIN_Y5]  # ОЦЕНКА (година 5 = отраслова медиана)


def dcf(rate):
    rev, pv, flows = HYPO["revenue"], 0.0, []
    for y, (g, m) in enumerate(zip(GROWTH, MARGINS), start=1):
        rev *= 1 + g
        fcf = rev * m  # ОЦЕНКА: свободен паричен поток ≈ EBITDA (без капиталови разходи и оборотен капитал)
        pv += fcf / (1 + rate) ** y
        flows.append((y, round(rev), round(fcf)))
    tv = rev * MARGINS[-1] * EV_EBITDA
    pv += tv / (1 + rate) ** 5
    return pv, flows, tv


def valuation(u_base, u_opt):
    r = HYPO["revenue"]
    comps = {k: v * r for k, v in DEALS.items()}
    m = sorted(DEALS.values())
    per_cust = {"base": u_base["ltv24"] * HYPO["customers"], "opt": u_opt["ltv24"] * HYPO["customers"]}
    d = {rate: dcf(rate)[0] for rate in (0.50, 0.60, 0.70)}
    ranges = {
        "Сравними сделки (EV/приходи)": (m[0] * r, m[1] * r, m[2] * r),
        "Множител на клиент (LTV 24м)": (max(per_cust["base"], 0), (max(per_cust["base"], 0) + per_cust["opt"]) / 2, per_cust["opt"]),
        "Дисконтирани парични потоци": (d[0.70], d[0.60], d[0.50]),
    }
    low = min(v[0] for v in ranges.values())
    mid = statistics.median([v[1] for v in ranges.values()])
    high = max(v[2] for v in ranges.values())
    pre_money_ask = HYPO["ask"] / HYPO["stake"] - HYPO["ask"]
    rows = [[k, round(a), round(b), round(c)] for k, (a, b, c) in ranges.items()]
    rows.append(["ОБЩО (мин / медиана на средните / макс)", round(low), round(mid), round(high)])
    rows.append(["Искана pre-money оценка", round(pre_money_ask), "", ""])
    write_csv("valuation.csv", ["метод", "ниска €", "средна €", "висока €"], rows)
    _, flows, tv = dcf(0.60)
    write_csv("dcf_flows.csv", ["година", "приходи €", "FCF≈EBITDA €"], flows + [["терминална стойност (год. 5)", "", round(tv)]])
    return ranges, (low, mid, high), pre_money_ask, comps


# ---------- 5. Графики ----------
def fig_market(bu, td):
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.2))
    labels = [SCEN_BG[s] for s in SCEN]
    axes[0].bar(labels, [bu[s]["value_eur"] / 1e6 for s in SCEN], color=[LIGHT, BLUE, LIGHT], width=0.55)
    axes[0].set_title("Отдолу нагоре, ЕС (млн €)", fontsize=10, loc="left")
    axes[1].bar(labels, [td[s] * 1000 for s in SCEN], color=[LIGHT, ORANGE, LIGHT], width=0.55)
    axes[1].set_title("Отгоре надолу, Европа (млн $)", fontsize=10, loc="left")
    for ax, vals in ((axes[0], [bu[s]["value_eur"] / 1e6 for s in SCEN]), (axes[1], [td[s] * 1000 for s in SCEN])):
        for i, v in enumerate(vals):
            ax.text(i, v, f"{v:,.0f}".replace(",", " "), ha="center", va="bottom", fontsize=9)
        ax.grid(axis="x", visible=False)
    fig.suptitle("Отгоре надолу дава ~3 пъти повече: включва синтетика и всички купувачи", fontsize=11, x=0.02, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "01_pazar.png"))
    plt.close(fig)


def fig_competitors():
    # Цени на редовна цена (€), research/03_konkurenti_ceni.md; фокус по материал: 0 = рециклирана синтетика,
    # 1 = мерино + синтетика, 2 = предимно естествени влакна (по описанията в research/03 и 07).
    pts = [
        ("Organic Basics клин", 0, 75), ("Organic Basics клин", 0, 86),
        ("super.natural клин", 1, 79.99), ("super.natural клин", 1, 100),
        ("Icebreaker клин", 2, 99.90), ("Icebreaker клин", 2, 105.95),
        ("Ortovox тениска", 2, 74.90), ("Ortovox дълъг ръкав", 2, 89.90),
        ("Engel бельо", 2, 36.89), ("Engel бельо", 2, 47.50),
        ("Smartwool сутиен", 2, 64.95), ("Smartwool сутиен", 2, 69.95),
    ]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    seen = set()
    for name, x, y in pts:
        jitter = {"Organic Basics клин": -0.08, "super.natural клин": 0, "Icebreaker клин": 0.12,
                  "Ortovox тениска": -0.12, "Ortovox дълъг ръкав": -0.12, "Engel бельо": 0.0, "Smartwool сутиен": 0.24}[name]
        ax.scatter(x + jitter, y, s=60, color=GRAY if "бельо" in name else BLUE, edgecolor="white", linewidth=1.5, zorder=3)
        if name not in seen:
            ax.annotate(name, (x + jitter, y), xytext=(8, 0), textcoords="offset points", fontsize=8, va="center")
            seen.add(name)
    ax.text(0.55, 55, "празно: клин с естествени\nвлакна под €79.99", fontsize=8, color=INK, va="center",
            bbox=dict(boxstyle="round", fc="#fbe1d6", ec="none"))
    ax.set_xticks([0, 1, 2], ["рециклирана синтетика", "мерино + синтетика", "предимно естествени"])
    ax.set_xlim(-0.5, 2.9)
    ax.set_ylim(20, 120)
    ax.set_ylabel("редовна цена, € (с ДДС)")
    ax.set_title("Клин с мерино: от €79.99 (смес); предимно естествен: от €99.90", fontsize=11, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "02_konkurenti.png"))
    plt.close(fig)


def fig_unit(u):
    steps = [("Нетна цена", u["net"]), ("Себестойност", -(u["net"] - u["margin"])),
             ("Връщания", -(u["margin"] - u["kept"])), ("Плащане", -u["pay"]),
             ("Доставка\n+ връщане", -(u["ship"] + u["ret_ship"]))]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    run = 0
    for i, (lab, v) in enumerate(steps):
        bottom = run if v >= 0 else run + v
        ax.bar(i, abs(v), bottom=bottom, color=BLUE if i == 0 else LIGHT, width=0.6)
        ax.text(i, run + v if v >= 0 else run, f"{v:+.1f}", ha="center", va="bottom", fontsize=8)
        run += v
    i = len(steps)
    ax.bar(i, u["contrib"], color=BLUE, width=0.6)
    ax.text(i, u["contrib"], f"{u['contrib']:.1f}", ha="center", va="bottom", fontsize=8)
    ax.bar(i + 1, u["cac"], color=ORANGE, width=0.6)
    ax.text(i + 1, u["cac"], f"{u['cac']:.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(i + 2), [s[0] for s in steps] + ["Принос на\nпоръчка", "CAC"], fontsize=8)
    ax.set_ylabel("€ на поръчка")
    ax.grid(axis="x", visible=False)
    ax.set_title("Базов сценарий: една поръчка носи по-малко, отколкото струва клиентът", fontsize=11, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "03_ikonomika.png"))
    plt.close(fig)


def fig_cash(paths):
    fig, ax = plt.subplots(figsize=(8, 3.4))
    colors = {"pess": GRAY, "base": BLUE, "opt": ORANGE}
    for s in SCEN:
        ax.plot(range(len(paths[s])), [v / 1000 for v in paths[s]], color=colors[s], linewidth=2, label=SCEN_BG[s])
        ax.annotate(SCEN_BG[s], (len(paths[s]) - 1, paths[s][-1] / 1000), xytext=(4, 0), textcoords="offset points", fontsize=8, va="center")
    ax.axhline(-50, color=INK, linewidth=1, linestyle="--")
    ax.text(24, -42, "−50 000 € (инвестицията)", fontsize=8, va="bottom")
    ax.set_xlabel("месец")
    ax.set_ylabel("натрупан паричен поток, хил. €")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_title("Само оптимистичният сценарий връща парите: на 9-ия месец", fontsize=11, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "04_scenarii.png"))
    plt.close(fig)


def fig_tornado(base_val, rows):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    rows = rows[::-1]
    for i, (lab, lo, hi) in enumerate(rows):
        ax.barh(i, lo, color=GRAY, height=0.55)
        ax.barh(i, hi, color=BLUE, height=0.55)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.axvline(0, color=INK, linewidth=1)
    ax.set_xlabel(f"промяна на печалбата от клиент за 24 мес., € (база {base_val:.1f} €; сиво = −20%, синьо = +20%)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Маржът, цената и конверсията движат резултата най-много", fontsize=11, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "05_chuvstvitelnost.png"))
    plt.close(fig)


def fig_valuation(ranges, total, ask):
    fig, ax = plt.subplots(figsize=(8, 2.8))
    names = list(ranges.keys())
    for i, n in enumerate(names):
        lo, mid, hi = ranges[n]
        ax.plot([lo / 1000, hi / 1000], [i, i], color=LIGHT, linewidth=10, solid_capstyle="round")
        ax.scatter(mid / 1000, i, color=BLUE, s=60, zorder=3)
    ax.axvline(ask / 1000, color=ORANGE, linewidth=2)
    ax.text(ask / 1000 - 8, len(names) - 0.4, f"искана pre-money {ask/1000:.0f} хил. €", color=INK, fontsize=8, ha="right")
    ax.set_yticks(range(len(names)), names)
    ax.set_ylim(-0.6, len(names))
    ax.set_xlabel("оценка на стартъпа, хил. €")
    ax.grid(axis="y", visible=False)
    ax.set_title("Исканата цена е над средата на всеки от трите метода", fontsize=11, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "06_ocenka.png"))
    plt.close(fig)


def main():
    p = load_params()
    bu, td, shares, sust = market(p)
    U = {s: unit(p[s]) for s in SCEN}
    paths, sims = {}, {}
    for s in SCEN:
        path, monthly, be, n_new = simulate(p[s], U[s])
        paths[s] = path
        sims[s] = dict(be_month=be, n_new=n_new, min_cash=min(path), end_cash=path[-1],
                       payback=next((i for i, v in enumerate(path) if i > 0 and v >= 0), None))
    rows = []
    keys = [("net", "нетна цена €"), ("margin", "брутна печалба €"), ("contrib", "принос на поръчка (след връщания, плащане, доставка) €"),
            ("cac", "CAC €"), ("ltv12", "стойност на клиента 12 мес. €"), ("ltv24", "стойност на клиента 24 мес. €"),
            ("profit24", "печалба от клиент 24 мес. (LTV24 − CAC) €"), ("max_cac", "максимален CAC за рентабилност €"),
            ("fixed", "постоянни разходи €/мес."), ("be_customers", "нови клиенти/мес. за рентабилност (стабилно състояние)"),
            ("inventory", "първоначална стока €")]
    for k, lab in keys:
        rows.append([lab] + [("никога" if U[s][k] == float("inf") else round(U[s][k], 2)) for s in SCEN])
    rows.append(["нови клиенти/мес. при 2 000 € маркетинг"] + [round(sims[s]["n_new"], 1) for s in SCEN])
    rows.append(["първи месец с печалба (36 мес.)"] + [sims[s]["be_month"] or "няма" for s in SCEN])
    rows.append(["месец, в който натрупаният поток става ≥ 0"] + [sims[s]["payback"] or "няма за 36 мес." for s in SCEN])
    rows.append(["нужен капитал = най-ниска точка на натрупания поток (36 мес.) €"] + [round(-sims[s]["min_cash"]) for s in SCEN])
    rows.append(["натрупан поток след 36 мес. €"] + [round(sims[s]["end_cash"]) for s in SCEN])
    write_csv("unit_economics.csv", ["показател"] + [SCEN_BG[s] for s in SCEN], rows)
    write_csv("cashflow_36m.csv", ["месец"] + [SCEN_BG[s] for s in SCEN],
              [[i] + [round(paths[s][i]) for s in SCEN] for i in range(len(paths["base"]))])

    base_val, sens = sensitivity(p)
    ranges, total, ask, comps = valuation(U["base"], U["opt"])

    # Прагове „какво трябва да е вярно“ (базов сценарий, всяко поотделно)
    q = p["base"]
    ub = U["base"]
    cac_zero = ub["ltv24"]  # печалба 0 на клиент
    cac_ss = q["marketing"] * ub["ltv24"] / (q["marketing"] + ub["fixed"])  # покрива и постоянните разходи

    def payback_with_cac(cac):
        u2 = dict(ub, cac=cac)
        return simulate(q, u2)[0][-1] >= 0

    lo, hi = 0.01, cac_ss
    for _ in range(60):  # двоично търсене: най-висок CAC, при който натрупаният поток е ≥ 0 след 36 мес.
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if payback_with_cac(mid) else (lo, mid)
    cac_36 = lo
    orders_needed = ub["cac"] / ub["contrib"]
    one = lambda k, v: unit(dict(q, **{k: v}))
    thr = [
        ["CAC за печалба 0 на клиент (LTV24 = CAC) €", round(cac_zero, 2)],
        ["CAC, при който стабилният месечен резултат покрива и постоянните разходи €", round(cac_ss, 2)],
        ["CAC, при който парите се връщат до 36-ия месец €", round(cac_36, 2)],
        ["поръчки за 24 мес., при които LTV24 = CAC (базов CAC)", round(orders_needed, 2)],
        ["принос на поръчка при 42% връщания, останалото базово €", round(one("return_rate", 0.42)["contrib"], 2)],
        ["принос на поръчка при марж 41.0%, останалото базово €", round(one("gross_margin", 0.41)["contrib"], 2)],
    ]
    write_csv("thresholds.csv", ["праг", "стойност"], thr)

    # Двуседмичен тест: бюджет и праг = CAC за връщане на парите до 36 мес.
    test_budget = 600  # ОЦЕНКА
    clicks = test_budget / q["cpm"] * 1000 * q["ctr"]
    need_orders = -(-test_budget // cac_36)  # закръгляне нагоре
    write_csv("test_2w.csv", ["показател", "стойност"], [
        ["бюджет € (ОЦЕНКА)", test_budget], ["очаквани кликове при CPM и CTR базов", round(clicks)],
        ["праг 1: CAC за покриване на постоянните разходи €", round(cac_ss, 2)],
        ["праг 1: нужни поръчки (закръглено нагоре)", int(-(-test_budget // cac_ss))],
        ["праг 1: нужна конверсия", round(-(-test_budget // cac_ss) / clicks, 4)],
        ["праг 2: CAC за връщане на парите до 36 мес. €", round(cac_36, 2)],
        ["праг 2: нужни поръчки (закръглено нагоре)", int(need_orders)],
        ["праг 2: нужна конверсия = поръчки / кликове", round(need_orders / clicks, 4)]])

    # Цена за придобиване по канал (research/05_kanali_cac.md). Без превалутиране: курсът няма източник.
    g = p["base"]["price_gross"]
    write_csv("cac_by_channel.csv", ["канал", "сметка", "резултат", "валута", "бележка"], [
        ["Meta (базов)", "CPM 9.05 / (1000 × CTR 1.29% × CVR 1.9%)", round(U["base"]["cac"], 2), "EUR", "Германия; бенчмарк агенции"],
        ["Meta (оптимистичен)", "CPM 9.05 / (1000 × CTR 2.25% × CVR 2.9%)", round(U["opt"]["cac"], 2), "EUR", ""],
        ["Google Search", "CPC 4.44 / CVR 4.50%", round(4.44 / 0.045, 2), "USD", "данни за САЩ"],
        ["Amazon.de", "15% комисиона × цена 89", round(0.15 * g, 2), "EUR", "на поръчка, не на клиент; клиентът остава на Amazon"],
        ["Zalando", "5–25% × цена 89", f"{0.05 * g:.2f}–{0.25 * g:.2f}", "EUR", "на поръчка; комисиона от 2019"],
        ["Инфлуенсъри (микро)", "€250–2 500 на пост / брой продажби", "не е намерено", "EUR", "нужен тест: конверсията не е известна"],
        ["Бенчмарк смесен CAC apparel", "медиана на 35 марки", 58, "USD", "Eightx 2025; топ 10% $34, долни 10% $112"]])

    fig_market(bu, td)
    fig_competitors()
    fig_unit(U["base"])
    fig_cash(paths)
    fig_tornado(base_val, sens)
    fig_valuation(ranges, total, ask)
    print("готово:", sorted(os.listdir(OUT)), sorted(os.listdir(FIG)))


if __name__ == "__main__":
    main()
