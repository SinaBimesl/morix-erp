# Business Requirements

Source: `morix-erp.pdf` in the repository root. It is a single-page Figma
diagram (10128 × 3836 pt, created 2026-11-27) with Persian labels, some English
labels, and no other text.

It replaces an earlier, incorrect source (`morix-comp-1.pdf`). Nothing in
these documents is taken from that file.

Companion documents: [WORKFLOWS.md](WORKFLOWS.md) covers the process elements
the PDF shows, and [DOMAIN_MODEL.md](DOMAIN_MODEL.md) covers concepts and the
glossary.

## How to read this document

| Label | Meaning |
|---|---|
| **[PDF]** | Shown in the PDF: a box label, or an arrow between boxes. Text is quoted verbatim. |
| **[Interpretation]** | The minimum reading needed to use the diagram, such as "an empty box is a placeholder". It is not written in the PDF. |

These documents contain no assumptions and no recommendations. Anything the
PDF does not show is listed as an open question in §5. Translations from
Persian are ours. Unclear labels keep their original text and are listed in
§6.

---

## 1. What the PDF contains

**[PDF]** Eleven green top-level boxes. None of them is connected to another,
and there is no company root box.

| # | Persian | English | Detail in the PDF |
|---|---|---|---|
| 1 | تعمیر و سرویس | Repair and Service | Item tree plus six services |
| 2 | بخش رنگ | Paint Department | Four-level tree |
| 3 | ارتباط با مشتری | Customer Communication | Three-level tree |
| 4 | تولید | Production | Four-level tree |
| 5 | گارانتی | Warranty | Four child boxes, no further detail |
| 6 | مدیریت | Management | One empty child box |
| 7 | حسابداری | Accounting | One empty child box |
| 8 | فروش | Sales | One empty child box |
| 9 | CNC | CNC | One empty child box |
| 10 | خرید | Purchasing | One empty child box |
| 11 | نجاری | Carpentry | One empty child box |

**[Interpretation]** Box colours mark levels. There is no legend:
- green: top-level area;
- purple: category;
- red: sub-category or item group;
- white: leaf item or task.

Diamonds mark the repair services in §1.1.

**[Interpretation]** An empty box is a placeholder whose content is not yet
defined.

### 1.1 Repair and Service (تعمیر و سرویس)

**[PDF]** Items:

```
تعمیر و سرویس  Repair and Service
├── گیتار  Guitar
│   ├── الکتریک  Electric
│   ├── باس  Bass
│   ├── کلاسیک  Classical
│   └── آکوستیک  Acoustic
├── آمپلی فایر  Amplifier            (no children)
└── تجهیزات جانبی  Accessory equipment
    └── افکت و یونیت  Effects and units
```

**[PDF]** Six services are drawn as diamonds below the guitar types. Arrows
run from each service to **each of the four guitar types**. This was checked
against the PDF's vector paths: every service has four connectors, one per
type. No service connects to Amplifier or Accessory equipment.

| Persian | English | Diamond colour |
|---|---|---|
| ارتقا ساز | Instrument upgrade | Pink |
| رگلاژ عمومی | General setup (adjustment) | White |
| فرت لول | Fret levelling | Green |
| تعمیر و ارتقا الکترونیک | Electronics repair and upgrade | Teal |
| ری فرت | Refret | White |
| ترمیم رنگ | Paint/finish repair | White |

The diamond colours have no legend; their meaning is unknown (§6).

### 1.2 Paint Department (بخش رنگ)

**[PDF]**

```
بخش رنگ  Paint Department
├── نگهداری تجهیزات  Equipment maintenance
│   ├── کمپرسور  Compressor
│   │   ├── بررسی روغن  Oil check
│   │   ├── بررسی تسمه  Belt check
│   │   ├── فیلتر هوا  Air filter
│   │   └── بررسی اتصالات  Connections/fittings check
│   ├── پیستوله  Spray gun
│   │   └── تمیز کاری و بررسی  Cleaning and inspection
│   │       ├── شستشوی مخزن  Cup/tank washing
│   │       └── سوزن و کلاهک هوا  Needle and air cap
│   └── سیستم تهویه  Ventilation system
│       └── تمیزکاری و بررسی  Cleaning and inspection
├── تامین منابع  Resource supply
│   ├── ابزار پاشش  Spraying tools
│   │   └── پیستوله  Spray gun
│   ├── آماده سازی چوب  Wood preparation          (no children)
│   ├── تهیه اقلام رنگ  Paint materials supply
│   │   └── رنگ , کیلر , سیلر , هاردنر موشتابا دسین
│   │       Paint, clear coat (کیلر), sealer, hardener, "موشتابا دسین" (§6)
│   ├── ابزار پرداخت  Finishing tools
│   │   ├── سنباده  Sandpaper
│   │   └── پولیش و پد پولیش  Polish and polishing pads
│   ├── حلال ها  Solvents
│   │   └── تینر  Thinner
│   └── ایمنی و محیط کار  Safety and work environment
│       ├── دستکش  Gloves
│       ├── ماسک  Mask
│       └── عینک مخصوص  Special (safety) goggles
└── مدیریت  Management
    └── (empty box)
```

**[PDF]** A blue curved arrow runs from "ابزار پاشش" (Spraying tools, under
Resource supply) to "پیستوله" (Spray gun, under Equipment maintenance). It is
the only link between separate branches anywhere in the PDF.

**[Interpretation]** The supplied spray gun and the maintained spray gun are
the same equipment.

### 1.3 Customer Communication (ارتباط با مشتری)

**[PDF]**

```
ارتباط با مشتری  Customer Communication
├── شخص ثالث  Third party                (no children)
├── حضوری  In person
├── تلفنی  By phone
│   ├── زنگ  Call
│   └── پیامک  SMS
└── آنلاین  Online
    ├── سایت  Website
    ├── تلگرام  Telegram
    ├── اینستاگرام  Instagram
    ├── روبیکا  Rubika
    └── بله  Bale
```

### 1.4 Production (تولید)

**[PDF]** String counts, "passive", "active", and "RG10" are written in
English in the PDF.

```
تولید  Production
├── قطعات گیتار / لوازم جانبی  Guitar parts / Accessories   (one box, two lines; no children)
├── گیتار  Guitar
│   ├── الکتریک  Electric
│   │   ├── 6 string
│   │   ├── 7 string
│   │   └── 8 string
│   └── بیس  Bass
│       ├── 4 string
│       ├── 5 string
│       └── 6 string
├── آمپلی فایر  Amplifier
│   └── RG10
└── پری آمپ گیتار  Guitar preamp
    ├── گیتار بیس  Bass guitar
    │   └── passive
    │       └── بارتولینی  Bartolini
    └── گیتار الکتریک  Electric guitar
        └── active
```

**[PDF]** Production shows electric and bass guitars only. Classical and
acoustic, which appear under Repair, do not appear under Production.

### 1.5 Warranty (گارانتی)

**[PDF]**

```
گارانتی  Warranty
├── قطعات گیتار / لوازم جانبی  Guitar parts / Accessories
├── گیتار  Guitar
├── آمپلی فایر  Amplifier
└── پری آمپ گیتار  Guitar preamp
```

**[PDF]** These are the same four category names as the first level under
Production. No warranty terms, durations, or conditions are given.

---

## 2. Departments and areas

| Area | What the PDF defines |
|---|---|
| Repair and Service | Repairable item categories; six guitar services |
| Paint Department | Equipment and its maintenance tasks; supply categories and items; a Management sub-unit (empty) |
| Customer Communication | Contact channels |
| Production | Product categories and variants |
| Warranty | Categories covered |
| Management | Name only |
| Accounting | Name only |
| Sales | Name only |
| CNC | Name only |
| Purchasing | Name only |
| Carpentry | Name only |

**[PDF]** "Management" (مدیریت) appears twice: as a top-level area and as a
sub-unit of the Paint Department.

---

## 3. Products and services

| Item | Source |
|---|---|
| Produced guitars: electric (6, 7, 8 string), bass (6, 4, 5 string) | **[PDF]** §1.4 |
| Produced amplifier: RG10 | **[PDF]** §1.4 |
| Produced guitar preamps: for bass guitar (passive, Bartolini), for electric guitar (active) | **[PDF]** §1.4 |
| Produced guitar parts / accessories (no items listed) | **[PDF]** §1.4 |
| Warranty on guitar parts/accessories, guitars, amplifiers, guitar preamps | **[PDF]** §1.5 |
| Repair and service of guitars (electric, bass, classical, acoustic), amplifiers, and effects units | **[PDF]** §1.1 |
| Guitar services: instrument upgrade, general setup, fret levelling, electronics repair and upgrade, refret, paint/finish repair | **[PDF]** §1.1 |

---

## 4. Scope requirements

**[Interpretation]** Each requirement says only that the system must be able
to represent what the PDF lists. Behaviour beyond that is not specified by the
PDF; see §5. IDs are stable; refer to them in issues and commits.

| ID | Requirement | Source |
|---|---|---|
| BR-ORG-1 | Represent the eleven areas in §1, and the Paint sub-units: Equipment maintenance, Resource supply, Management. | §1, §1.2 |
| BR-REP-1 | Represent repairable items: Guitar (Electric, Bass, Classical, Acoustic), Amplifier, Accessory equipment (Effects and units). | §1.1 |
| BR-REP-2 | Represent the six guitar services, each applicable to all four guitar types. | §1.1 |
| BR-PNT-1 | Represent paint equipment (compressor, spray gun, ventilation system) and the maintenance tasks listed for each, including sub-tasks. | §1.2 |
| BR-PNT-2 | Represent paint supply categories and their items, as listed. | §1.2 |
| BR-PNT-3 | The spray gun as a supplied item and as maintained equipment refers to the same thing. | §1.2 arrow |
| BR-CUS-1 | Represent contact channels: third party; in person; phone (call, SMS); online (website, Telegram, Instagram, Rubika, Bale). | §1.3 |
| BR-PRD-1 | Represent product categories: guitar parts/accessories, guitar, amplifier, guitar preamp. | §1.4 |
| BR-PRD-2 | Represent guitar variants by type and string count: electric 6/7/8, bass 4/5/6. | §1.4 |
| BR-PRD-3 | Represent amplifier model RG10 and preamp variants (bass: passive, Bartolini; electric: active). | §1.4 |
| BR-WAR-1 | Represent warranty coverage for the four product categories. | §1.5 |

Note: the existing User Manager already supports a department tree
(`parent_id`) and teams (`CLAUDE.md`). BR-ORG-1 can be met with data.

---

## 5. Open questions

The PDF does not answer these:

1. **Production process.** How do Carpentry, CNC, and Paint relate to
   Production? Which steps, in which order? Built to order, to stock, or both?
2. **Production catalogue.** What items are under "Guitar parts /
   Accessories"? Is RG10 the only amplifier? Are there other guitar models?
3. **Preamps.** Is it correct that the bass preamp is passive and the
   electric one active? What does "Bartolini" refer to: a brand of part, a
   model, a supplier?
4. **Warranty.** Terms, durations, what is covered, and who handles claims.
   Does it cover only products the business produced, or sold, or also
   repairs?
5. **Repair process.** Intake, diagnosis, quote, approval, work, handover.
   Pricing for the six services.
6. **Services for non-guitar items.** The services connect only to guitars.
   What services exist for amplifiers and effects units?
7. **Placeholder areas.** What do Management, Accounting, Sales, CNC,
   Purchasing, Carpentry, and Paint Management do?
8. **Purchasing vs Resource supply.** Does the Paint Department buy its own
   supplies, or request them from Purchasing?
9. **Maintenance.** Intervals per task; whether results are recorded today.
10. **Third party channel.** Who is the third party: a reseller, an agent, a
    courier?
11. **Inventory.** Is there a warehouse? Which items are stocked?
12. **Money.** Currency, tax rules, invoicing, and accounting software.

## 6. Ambiguities in the source

| Text in PDF | Location | Issue |
|---|---|---|
| هاردنر موشتابا دسین | Paint → Paint materials supply | "Hardener" is clear. "موشتابا دسین" is not a recognised term: possibly a product or brand name, or a typo. |
| کیلر | Paint → Paint materials supply | Read as clear coat/lacquer. Confirm. |
| قطعات گیتار / لوازم جانبی | Production, Warranty | One box with two lines: one category, or two ("guitar parts" and "accessories")? |
| باس / بیس | Repair uses باس, Production uses بیس | Both mean "bass". Assumed to be the same type; confirm. |
| passive → بارتولینی | Production → Guitar preamp → Bass guitar | Bartolini sits below "passive" as a child. Whether it is a brand, model, or option is not shown. |
| RG10 | Production → Amplifier | Model name or code; not explained. |
| Diamond colours | Repair services | Pink, green, teal, and white. No legend. |
| Arrow colours | Production (red vs grey), Repair connectors | Probably styling only; no legend. |
| Empty boxes | Paint → Management; six top-level areas | Read as placeholders. |
| "Management" twice | Top level, and under Paint | Unclear whether they are related. |
| No links between areas | Whole page | No reporting lines or hand-offs are drawn, for example Production ↔ Carpentry/CNC/Paint, or Warranty ↔ Repair. |
