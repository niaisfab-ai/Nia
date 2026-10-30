# Бърз скрининг: спортни облекла от естествени материи, сертифицирани без BPA, PFAS и вредни химикали

*Дата: 30.10.2026 · Пазар: ЕС · Източниците са в `analysis/research/`, а сметките в `analysis/model.py` → `analysis/output/`.*

**Присъда: САМО АКО.** Проучваме задълбочено, само ако двуседмичен тест с €600 [ОЦЕНКА] реклама донесе поне 31 предварителни поръчки на клин за €89 [ОЦЕНКА]. Това означава CAC ≤ €19.69, при който бизнесът покрива и постоянните си разходи ([test_2w.csv](../analysis/output/test_2w.csv)). Нишата съществува: намерихме 8 марки, а спортните дрехи от естествени материи струват €64.95–105.95. В базовия сценарий обаче един клиент носи €31.37 за 24 месеца, а привличането му струва €36.92 ([unit_economics.csv](../analysis/output/unit_economics.csv)). Освен това „без PFAS“ става задължително във Франция и Дания от 2026, а в ЕС първо за PFHxA, така че спира да отличава марката.

## 1. Кой плаща, колко са и колко биха платили

| Стъпка | Стойност | Източник |
|---|---|---|
| Население на ЕС | 450.4 млн. души (01.01.2025) | Евростат чрез БТА, [01](../analysis/research/01_razmer_pazar.md) |
| Спортуват поне веднъж седмично | 38% от 26 580 анкетирани (15+) | Евробарометър SP525, 2022, [01](../analysis/research/01_razmer_pazar.md) |
| Купуват облекла онлайн | 46% от интернет потребителите | Евростат 2024, [09](../analysis/research/09_oficialni_fakti.md) |
| **Казват**, че биха платили повече за устойчиви продукти | 59% (72% през 2007) | Евробарометър/EEA 2024, [02](../analysis/research/02_klienti_tarsene.md) |
| **Реално** плащат премия за устойчиво облекло | 1–7% от ~19 000 анкетирани в 8 държави | BCG 2022 (медия), [02](../analysis/research/02_klienti_tarsene.md) |
| **Купувачи в ЕС** (450.4 млн × 38% × 46% × 1–7%) | **0.79–5.51 млн. души** (базов 3.15 млн при 4% [ОЦЕНКА]); горна граница, защото 38% е от хората на 15+ г., а 46% от интернет потребителите | [market_size.csv](../analysis/output/market_size.csv) |
| Колко плащат за клин от естествени материи | €75–109.52 редовна цена, медиана €99.90 от 7 цени | [03](../analysis/research/03_konkurenti_ceni.md) |
| Средна заявена премия за устойчиви стоки | 9.7% (PwC, >20 000 анкетирани в 31 държави) | [02](../analysis/research/02_klienti_tarsene.md) |

Демографията на купувачите в тази ниша **не е намерена**. Може да се събере с анкета сред 200–300 души от целевата група или от пълния доклад на Евробарометъра.

## 2. Кой вече го прави и на каква цена

| Марка | Материал | Цена (редовна) | Линк |
|---|---|---|---|
| Icebreaker (на VF Corp) | мерино | клин €99.90–105.95 | [Snowleader](https://www.snowleader.com/en/wmns-200-oasis-leggings-black-ICEB01206.html) |
| super.natural | мерино + технически влакна | клин €79.99–100 | [сайт](https://supernatural-merino.com/eu/Outlet/) |
| Ortovox | 52% вълна, 33% Tencel, 15% полиамид (модел Fast Upward LS) | тениска €74.90; дълъг ръкав €89.90 | [Hardloop](https://en.hardloop.de/product/60700-ortovox-120-cool-tec-mountain-cut-ts-merino-shirt-womens) |
| Engel Sports | вълна + коприна, GOTS | бельо €36.89–47.50 | [сравнение на цени](https://www.preissuchmaschine.de/preisvergleich/engel-damen-kurzarm-unterhemd-merino-500001116153.html) |
| Smartwool (на VF Corp) | мерино | спортен сутиен €64.95–69.95 | [smartwool.eu](https://smartwool.eu/re/women-s-intraknit-racerback-bra-12-13010.html) |
| Houdini | без PFAS от 2018 г. | клин €109.52 | [Outnorth](https://www.outnorth.com/int/brands/houdini/houdini-women-s-pace-trail-tights-true-black-FS585459) |
| Organic Basics | рециклиран найлон, TENCEL | клин €75–86 | [сайт](https://organicbasics.com/products/womens-active-flow-leggings-river) |
| Tripulse | TENCEL, OEKO-TEX 100, „plastic-free“ | цена: не е намерена | [сайт](https://tripulse.co/products/next-gen-sports-bra-with-tencel™) |

Българска марка за спортно облекло от естествени материи **не е намерена**. Намерена е само Stinky Socks, която прави само чорапи ([Capital](https://www.capital.bg/biznes/kompanii/2024/03/15/4598796_chorapi_za_djentulmeni/)).

## 3. Три сигнала за търсене

| Сигнал | Какво намерихме | Сила |
|---|---|---|
| Google Trends | **Не е намерено**: графиката не може да се прочете автоматично. Ръчна заявка: [trends.google.com](https://trends.google.com/trends/explore?date=today%205-y&q=PFAS%20free%20clothing,non%20toxic%20activewear,merino%20activewear,OEKO-TEX). Exploding Topics дава за „pfas-free“ 5.4K търсения и ръст +260% ([линк](https://explodingtopics.com/topic/pfas-free), мнение) | неизвестна |
| Обяви за работа | 2 примера: Gymshark (Materials Development Manager) и VF Corp (Product Sustainability). Общ брой **не е намерен** ([ImpactAlpha](https://impactalpha.com/?p=126780)) | слаба |
| Отзиви и реклами | Icebreaker има ~2K отзива в Trustpilot с оценка 4/5, а Smartwool 1.5/5 от 118. Броят активни реклами в Meta и Google **не е намерен** ([07](../analysis/research/07_otzivi_reklami.md)) | средна |

Сигнал отвъд трите: НПО тестове намират PFAS в 35 от 56 якета ([IPEN 2023](https://ipen.org/documents/toxics-our-clothing)) и BPA в спортни сутиени на 8 марки (2022) и клинове/шорти на 19 марки (2023) ([CEH](https://abc7.com/toxic-chemicals-athletic-wear-brands-watchdog-report-center-for-environmental-health/13267009/)). Осведомеността обаче е ниска: 6 от 10 германци не са чували за PFAS ([BfR 2024](https://www.bfr.bund.de/cm/364/bfr-consumer-monitor-02-2024.pdf)).

## 4. Най-големият риск

**„Без PFAS“ престава да е предимство, защото става задължително, първо в отделни държави и за подгрупи PFAS:**
- Франция забранява PFAS в облекла от 01.01.2026 ([FAQ на министерството](https://www.ecologie.gouv.fr/sites/default/files/documents/20260527_FAQ_decret_PFAS.pdf)).
- Дания ги забранява от 01.07.2026 ([SGS](https://www.sgs.com/en/news/2025/09/safeguards-14825-denmark-introduces-national-ban-on-pfas-in-clothing-and-footwear)).
- ЕС ограничава PFHxA (една подгрупа PFAS) в облеклата от 10.10.2026 ([B&D](https://www.bdlaw.com/publications/new-eu-pfhxa-limits-take-effect-amid-expanding-pfas-rules-for-apparel-and-textiles/)).
- Гласуването за пълно ограничение на PFAS се очаква в началото на 2027 г. ([EOG](https://www.europeanoutdoorgroup.com/members-knowledge-hub/echa-updates-pfas-restriction-process-and-timelines)).

Освен това от 27.09.2026 общите „зелени“ твърдения без удостоверяване са забранени (Директива 2024/825, [ЕК](https://circular-cities-and-regions.ec.europa.eu/support-materials/eu-regulations-legislation/directive-eu-2024825-empowering-consumers-green)). Остава отличителното „без BPA“: в ЕС още няма ограничение за BPA в текстила, а Германия подаде намерение за такова на 23.04.2026 ([UBA](https://www.umweltbundesamt.de/themen/reach-beschraenkungsdossier-fuer-bisphenole?parent=69322)).

## 5. Присъда

**САМО АКО** двуседмичен тест покаже CAC ≤ €19.69 при цена €89. Тестът: €600 реклами в Meta → очаквани 855 клика → нужни ≥31 предварителни поръчки, т.е. конверсия ≥3.62%. Ако поръчките са ≥46 (конверсия ≥5.38%, CAC ≤ €13.09), парите се връщат до 36-ия месец ([test_2w.csv](../analysis/output/test_2w.csv)). Типичната конверсия на модни магазини е 1.9% ([05](../analysis/research/05_kanali_cac.md)), така че прагът е висок. Ако тестът мине, продължаваме по [пълния анализ](Спортни%20облекла.md). Ако не мине, спираме и сме похарчили €600 вместо €50 000.

**Липсва:** Google Trends по държави; броят активни реклами на конкурентите; демографията на нишата; реални оферти за плат и шиене. Първите две се събират ръчно в браузър за около 1 час.
