# Детайлен скрининг: приложение за управление на абонаменти с прекратяване при смърт от доверени роднини

*Дата: 13.11.2026 · Пазар: глобален · Източници: `analysis/abonamenti/research/` · Сметки: `analysis/abonamenti/model.py` · Суми в USD, без превалутиране. [ОЦЕНКА] означава допускане.*

**Присъда: САМО АКО.** Проучваме задълбочено, само ако двуседмичен тест покаже две неща:
- CAC ≤ $21,02: от $600 [ОЦЕНКА] реклама поне 29 платени предварителни поръчки за $5,99 на месец [ОЦЕНКА] ([test_2w.csv](../analysis/abonamenti/output/test_2w.csv));
- поне 2 писма за намерение от застраховател, банка или погребална агенция [ОЦЕНКА].

Нишата съществува, но е разцепена на две:
- **Управление на абонаменти:** платена и голяма. Rocket Money има 4 583 (по 10-K, вероятно хиляди) платени абонати.
- **„При смърт“:** безплатна за семействата. Life Ledger, Settld, Tell Us Once, Apple и Google не таксуват семействата, а печелят от бизнеса.

## 1. Кой плаща, колко са и колко биха платили

| Сегмент | Колко са | Колко плащат | Източник |
|---|---|---|---|
| Живи потребители с много абонаменти | 42% от 1 000 американци са забравили абонамент; реалният разход е $219/мес. срещу предполагаемите $86 (2022) | Rocket Money Premium $6–12/мес.; Emma £4,99–14,99/мес.; Monarch $99,99/год. | C+R Research ([01](../analysis/abonamenti/research/01_razmer_pazar.md)); [03](../analysis/abonamenti/research/03_konkurenti_ceni.md) |
| Семейства след смърт | 8 461 279 починали годишно (САЩ 3 072 666, Англия и Уелс 568 613, ЕС 4 820 000; 2024). Опечалените се свързват средно с 6,4 организации (2 500 анкетирани, 2023) | от $0 (Life Ledger, Settld) до $149 първата година (GoodTrust) | CDC, ONS, Евростат ([09](../analysis/abonamenti/research/09_oficialni_fakti.md)); Marie Curie ([02](../analysis/abonamenti/research/02_klienti_tarsene.md)) |
| Бизнеси (застрахователи, банки) | Empathy работи с New York Life, MetLife, The Hartford; Settld със Starling | цените не са публични | [05](../analysis/abonamenti/research/05_kanali_cac.md) |
| **Платени семейства (отдолу нагоре)** | 253 838 случая годишно = 3% [ОЦЕНКА] от починалите (1–10%) | $25,4 млн. годишно ($5,5–126,1 млн.) [ОЦЕНКА] | [market_bottom_up.csv](../analysis/abonamenti/output/market_bottom_up.csv) |

Готовност да се плати за функция „при смърт“ **не е намерена** в нито едно проучване ([02](../analysis/abonamenti/research/02_klienti_tarsene.md)).

## 2. Кой вече го прави и на каква цена

| Марка | Какво прави | Цена | Линк |
|---|---|---|---|
| Rocket Money (САЩ) | открива и прекратява абонаменти (concierge в Premium) | $6–12/мес. по избор | [rocketmoney.com](https://www.rocketmoney.com/learn/personal-finance/how-much-does-rocket-money-cost) |
| Monarch (САЩ) | бюджет, засича повтарящи се плащания | $99,99/год. или $14,99/мес. | [Toolradar](https://toolradar.com/tools/monarch-money/pricing.md) |
| Emma (UK) | бюджет и абонаменти | £4,99–14,99/мес. | [European Purpose](https://europeanpurpose.com/tool/emma-app) |
| Bobby (iOS) | ръчен тракер на абонаменти | безплатно до 5; $1,99 еднократно | [App Pricing Lab](https://apppricinglab.com/iap/apple/1059152023) |
| GoodTrust (САЩ) | дигитален наследствен план + прекратяване при смърт | $149 първа година, после $39/год. | [GoodTrust](https://support.mygoodtrust.com/support/solutions/articles/66000513649-how-much-does-goodtrust-cost-) |
| Everplans (САЩ) | дигитален сейф с доверени лица | безплатно до 10 записа; $99,99/год. | [Everplans](https://www.everplans.com/pricing) |
| Life Ledger (UK) | уведомява 700–1 000+ фирми при смърт | безплатно за опечалените | [At a Loss](https://www.ataloss.org/life-ledger-estate-planning) |
| Settld (UK) | уведомява 970–1 400+ доставчици | безплатно за семействата, плащат професионалистите | [Today's Wills & Probate](https://todayswillsandprobate.co.uk/bereavement-account-settling-service/) |

Никой от управляващите абонаменти няма потвърдена функция „при смърт“. Сред услугите за смърт само GoodTrust сама прекратява абонаменти ([03](../analysis/abonamenti/research/03_konkurenti_ceni.md)).

## 3. Три сигнала за търсене

| Сигнал | Какво намерихме | Сила |
|---|---|---|
| Google Trends | **Не е намерено**: графиката не може да се прочете. Ръчно: [заявка](https://trends.google.com/trends/explore?date=today%205-y&q=cancel%20subscriptions,subscription%20manager,digital%20legacy) | неизвестна |
| Обяви за работа | Empathy: Care Manager ($24–26/час), Account Executive, Head of People; 3 отворени дистанционни позиции към 08.2026 (по брояч на трета страна). Life Ledger, Settld: не е намерено | слаба |
| Отзиви и реклами | Rocket Money: 4 126 отзива в Trustpilot (3,2/5); Monarch: 4,9 в App Store при 60–101 хил. оценки (по трети страни); Settld и Life Ledger: 48–60 отзива с 4,3–4,6. Реклами в Meta/Google: **не е намерено** | средна за абонаментите, слаба за „при смърт“ |

Източници: [02](../analysis/abonamenti/research/02_klienti_tarsene.md), [07](../analysis/abonamenti/research/07_otzivi_reklami.md).

## 4. Най-големият риск

**Никой не плаща за „при смърт“, а законът сам решава част от проблема.**
- Семействата получават функцията безплатно (Life Ledger, Settld, Tell Us Once, Apple, Google).
- ЕС въвежда бутон за оттегляне от 19.06.2026, Германия има бутон за прекратяване от 01.07.2022, а Великобритания въвежда абонаментни правила от януари 2027 (по медии) ([04](../analysis/abonamenti/research/04_regulacii.md)).
- Правото на роднините да прекратяват договори се различава по държави, а за България **не е намерено** ([04](../analysis/abonamenti/research/04_regulacii.md)).

## 5. Присъда

**САМО АКО** двуседмичният тест даде:
- ≥29 платени предварителни поръчки от $600 реклама (CAC ≤ $21,02, [thresholds.csv](../analysis/abonamenti/output/thresholds.csv));
- ≥2 писма за намерение от бизнеси.

Ако едното липсва, спираме. Пълният анализ е в [Абонаменти.md](Абонаменти.md).

**Липсва:** Google Trends, реклами на конкурентите, готовност да се плати, комисиони в B2B и правото на роднините в България.
