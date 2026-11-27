# Business Requirements

Source: `morix-erp.pdf` in the repository root. It is a single-page Figma
diagram (10128 × 3836 pt, created 2026-11-27) with Persian labels, some English
labels, and no other text. Clarifications from the business owner are recorded
in §2.

It replaces an earlier, incorrect source (`morix-comp-1.pdf`). Nothing in
these documents is taken from that file.

Companion documents: [WORKFLOWS.md](WORKFLOWS.md) covers the process elements
the PDF shows, and [DOMAIN_MODEL.md](DOMAIN_MODEL.md) covers concepts and the
glossary.

## How to read this document

| Label | Meaning |
|---|---|
| **[PDF]** | Shown in the PDF: a box label, or an arrow between boxes. Text is quoted verbatim. |
| **[Owner]** | Confirmed by the business owner. Each one has an ID (C1, C2, ...) listed in §2. |
| **[Interpretation]** | The minimum reading needed to use the diagram, such as "an empty box is a placeholder". Neither the PDF nor the owner states it. |

These documents contain no assumptions and no recommendations. Anything that
neither the PDF nor the owner answers is an open question in §6. Translations
from Persian are ours. Unclear labels keep their original text and are listed
in §7.

**Terminology.** "Bass Guitar" is the standard English term for both باس and
بیس (C1). "Guitar Parts and Accessories" is one category (C2).

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
│   ├── باس  Bass Guitar (C1)
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

The diamond colours have no legend; their meaning is unknown (§7).

**[Owner]** C6: Classical and acoustic guitars are not manufactured, but they
may be included in repair services.

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
│   │       Paint, clear coat, sealer, hardener (C5), "موشتابا دسین" (§7)
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

**[Owner]** C5: Clear coat (کیلر), hardener (هاردنر), and sealer (سیلر) are
materials used in the painting and finishing process.

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

**[Owner]** C7: Customers do not access MorixERP. None of these channels is a
way for customers to use the system.

### 1.4 Production (تولید)

**[PDF]** String counts, "passive", "active", and "RG10" are written in
English in the PDF.

```
تولید  Production
├── قطعات گیتار / لوازم جانبی  Guitar Parts and Accessories (C2)   (no children)
├── گیتار  Guitar
│   ├── الکتریک  Electric
│   │   ├── 6 string
│   │   ├── 7 string
│   │   └── 8 string
│   └── بیس  Bass Guitar (C1)
│       ├── 4 string
│       ├── 5 string
│       └── 6 string
├── آمپلی فایر  Amplifier
│   └── RG10  amplifier model (C4)
└── پری آمپ گیتار  Guitar preamp
    ├── گیتار بیس  Bass Guitar (C1)
    │   └── passive
    │       └── بارتولینی  Bartolini, a preamp type (C3)
    └── گیتار الکتریک  Electric Guitar
        └── active
```

**[Owner]** C6: Production is limited to electric guitars and bass guitars.
Classical and acoustic guitars are not manufactured by this workshop.

The PDF's Production tree also contains Amplifier, Guitar preamp, and Guitar
Parts and Accessories. How these relate to C6 is open (§6, question 1).

### 1.5 Warranty (گارانتی)

**[PDF]**

```
گارانتی  Warranty
├── قطعات گیتار / لوازم جانبی  Guitar Parts and Accessories (C2)
├── گیتار  Guitar
├── آمپلی فایر  Amplifier
└── پری آمپ گیتار  Guitar preamp
```

**[PDF]** These are the same four category names as the first level under
Production. No warranty terms, durations, or conditions are given.

---

## 2. Owner-confirmed clarifications

Confirmed by the business owner on 2026-11-27. They answer questions the PDF
left open; they do not change what the PDF shows.

| ID | Clarification | Applies to |
|---|---|---|
| C1 | "باس" and "بیس" refer to the same instrument: the bass guitar. The standard term is **Bass Guitar**. | §1.1, §1.4 |
| C2 | Guitar parts and accessories (قطعات گیتار / لوازم جانبی) are **one combined category**, not two. | §1.4, §1.5 |
| C3 | Bartolini (بارتولینی) refers to a specific **type of preamp** in this context. It is not classified as a brand or model. | §1.4 |
| C4 | RG10 is an **amplifier model**. | §1.4 |
| C5 | Clear coat (کیلر), hardener (هاردنر), and sealer (سیلر) are **materials used in the painting and finishing process**. | §1.2 |
| C6 | Production is limited to **electric guitars and bass guitars**. Classical and acoustic guitars are not manufactured by this workshop. They may still be included in repair services. | §1.1, §1.4 |
| C7 | MorixERP is an **internal workshop management system used by workshop managers**. Customers do not access it. Customer-facing portals, public interfaces, and customer accounts are not requirements. | Whole system |

---

## 3. Departments and areas

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

## 4. Products and services

| Item | Source |
|---|---|
| Manufactured guitars: electric (6, 7, 8 string) and Bass Guitar (4, 5, 6 string) only | **[PDF]** §1.4; **[Owner]** C1, C6 |
| Classical and acoustic guitars: not manufactured | **[Owner]** C6 |
| Amplifier model RG10, under Production | **[PDF]** §1.4; **[Owner]** C4 |
| Guitar preamps under Production: for Bass Guitar (passive, Bartolini preamp type), for electric guitar (active) | **[PDF]** §1.4; **[Owner]** C1, C3 |
| Guitar Parts and Accessories, one category under Production (no items listed) | **[PDF]** §1.4; **[Owner]** C2 |
| Warranty on Guitar Parts and Accessories, guitars, amplifiers, guitar preamps | **[PDF]** §1.5; **[Owner]** C2 |
| Repair and service of guitars (electric, Bass Guitar, classical, acoustic), amplifiers, and effects units | **[PDF]** §1.1; **[Owner]** C1, C6 |
| Guitar services: instrument upgrade, general setup, fret levelling, electronics repair and upgrade, refret, paint/finish repair | **[PDF]** §1.1 |
| Painting and finishing materials: paint, clear coat, sealer, hardener | **[PDF]** §1.2; **[Owner]** C5 |

---

## 5. Scope requirements

**[Interpretation]** Each BR requirement says only that the system must be
able to represent what the PDF lists. **[Owner]** requirements come directly
from §2. Behaviour beyond this is not specified; see §6. IDs are stable; refer
to them in issues and commits.

| ID | Requirement | Source |
|---|---|---|
| BR-SYS-1 | MorixERP is an internal system used by workshop managers. There are no customer-facing portals, public interfaces, or customer accounts. | **[Owner]** C7 |
| BR-ORG-1 | Represent the eleven areas in §1, and the Paint sub-units: Equipment maintenance, Resource supply, Management. | §1, §1.2 |
| BR-REP-1 | Represent repairable items: Guitar (Electric, Bass Guitar, Classical, Acoustic), Amplifier, Accessory equipment (Effects and units). | §1.1; C1, C6 |
| BR-REP-2 | Represent the six guitar services, each applicable to all four guitar types. | §1.1 |
| BR-PNT-1 | Represent paint equipment (compressor, spray gun, ventilation system) and the maintenance tasks listed for each, including sub-tasks. | §1.2 |
| BR-PNT-2 | Represent paint supply categories and their items, as listed. Clear coat, sealer, and hardener are painting and finishing materials. | §1.2; C5 |
| BR-PNT-3 | The spray gun as a supplied item and as maintained equipment refers to the same thing. | §1.2 arrow |
| BR-CUS-1 | Represent contact channels: third party; in person; phone (call, SMS); online (website, Telegram, Instagram, Rubika, Bale). These are not ways for customers to access the system. | §1.3; C7 |
| BR-PRD-1 | Represent the Production categories: Guitar Parts and Accessories (one category), Guitar, Amplifier, Guitar preamp. | §1.4; C2 |
| BR-PRD-2 | Manufactured guitars are electric (6/7/8 string) and Bass Guitar (4/5/6 string) only. | §1.4; C1, C6 |
| BR-PRD-3 | Represent amplifier model RG10 and the preamp variants: Bass Guitar passive with the Bartolini preamp type; electric guitar active. | §1.4; C3, C4 |
| BR-WAR-1 | Represent warranty coverage for the four categories in §1.5. | §1.5; C2 |

Note: the existing User Manager already supports a department tree
(`parent_id`) and teams (`CLAUDE.md`). BR-ORG-1 can be met with data.

---

## 6. Open questions

Neither the PDF nor the owner has answered these:

1. **Production scope vs C6.** C6 limits production to electric and bass
   guitars. The PDF's Production tree also lists an amplifier (RG10), guitar
   preamps, and Guitar Parts and Accessories. Are these manufactured too, or
   listed under Production for another reason?
2. **Production process.** How do Carpentry, CNC, and Paint relate to
   Production? Which steps, in which order? Built to order, to stock, or both?
3. **Production catalogue.** What items are in Guitar Parts and Accessories?
   Are there amplifier models besides RG10?
4. **Preamps.** Is it correct that Bass Guitar preamps are passive and
   electric-guitar preamps active, as drawn? Are there preamp types besides
   Bartolini?
5. **System users.** C7 names workshop managers as the users. Do any other
   staff (technicians, accounting, sales) log in? The existing User Manager
   allows staff accounts without an email address.
6. **Warranty.** Terms, durations, what is covered, and who handles claims.
   Does it cover only products the workshop produced, or sold, or also
   repairs?
7. **Repair process.** Intake, diagnosis, quote, approval, work, handover.
   Pricing for the six services.
8. **Services for non-guitar items.** The services connect only to guitars.
   What services exist for amplifiers and effects units?
9. **Placeholder areas.** What do Management, Accounting, Sales, CNC,
   Purchasing, Carpentry, and Paint Management do?
10. **Purchasing vs Resource supply.** Does the Paint Department buy its own
    supplies, or request them from Purchasing?
11. **Maintenance.** Intervals per task; whether results are recorded today.
12. **Third party channel.** Who is the third party: a reseller, an agent, a
    courier?
13. **Inventory.** Is there a warehouse? Which items are stocked?
14. **Money.** Currency, tax rules, invoicing, and accounting software.

## 7. Ambiguities in the source

Still unresolved:

| Text in PDF | Location | Issue |
|---|---|---|
| موشتابا دسین | Paint → Paint materials supply, after "هاردنر" | Not a recognised term: possibly a product or brand name, or a typo. C5 confirms hardener but not this text. |
| Diamond colours | Repair services | Pink, green, teal, and white. No legend. |
| Arrow colours | Production (red vs grey), Repair connectors | Probably styling only; no legend. |
| Empty boxes | Paint → Management; six top-level areas | Read as placeholders. |
| "Management" twice | Top level, and under Paint | Unclear whether they are related. |
| No links between areas | Whole page | No reporting lines or hand-offs are drawn, for example Production ↔ Carpentry/CNC/Paint, or Warranty ↔ Repair. |

Resolved by the owner (§2): باس / بیس (C1); قطعات گیتار / لوازم جانبی (C2);
بارتولینی (C3); RG10 (C4); کیلر, سیلر, هاردنر (C5).
