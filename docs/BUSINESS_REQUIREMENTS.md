# Business Requirements

Source: `morix-comp-1.pdf` in the repository root. It is a single-page Figma
diagram (created 2026-10-24) with Persian labels and no other text.

Companion documents: [WORKFLOWS.md](WORKFLOWS.md) covers processes and
[DOMAIN_MODEL.md](DOMAIN_MODEL.md) covers entities and the glossary.

## How to read this document

Every statement carries one of these labels:

| Label | Meaning |
|---|---|
| **[PDF]** | Shown in the PDF: a box label, or an arrow between boxes. Persian text is quoted verbatim. |
| **[Interpretation]** | A direct reading of what the PDF shows, such as "this box is a placeholder". It is not stated in the PDF. |
| **[Assumption]** | Not in the PDF. A working assumption based on common ERP practice or on `CLAUDE.md`. It must be confirmed before anyone builds on it. |
| **[Recommendation]** | A proposal for the system. It is not a requirement until the business approves it. |

Translations from Persian are ours. Where a label is unclear, the
original text is kept and the term is listed under [Ambiguities](#6-ambiguities-in-the-source).

---

## 1. What the PDF contains

**[PDF]** The page holds nine top-level green boxes. They are not connected to
each other, and there is no company root box. Six of them are drawn in full:

| # | Persian | English | Detail in the PDF |
|---|---|---|---|
| 1 | تعمیر و سرویس | Repair and Service | Three-level tree |
| 2 | بخش رنگ | Paint Department | Four-level tree |
| 3 | ارتباط با مشتری | Customer Communication | Three-level tree |
| 4 | فروش | Sales | One empty child box |
| 5 | مدیریت | Management | One empty child box |
| 6 | حسابداری | Accounting | One empty child box |
| 7 | نجاری | Carpentry (woodworking) | One empty child box |
| 8 | CNC | CNC machining | One empty child box |
| 9 | خرید | Purchasing | One empty child box |

**[Interpretation]** The colours encode levels. There is no legend:
- green: department or top-level area;
- purple: sub-area or category;
- red: item group or activity;
- white: concrete item or task (leaf).

**[Interpretation]** An empty box is a placeholder whose content has not been
defined yet. Departments 4 to 9 are named but not described.

**[Interpretation]** The file name `morix-comp-1` suggests "Morix company,
version 1": an early draft of the company structure, not a complete
specification.

### 1.1 Repair and Service (تعمیر و سرویس)

**[PDF]**

```
تعمیر و سرویس  Repair and Service
├── گیتار  Guitar
│   ├── الکتریک  Electric
│   ├── باس  Bass
│   ├── کلاسیک  Classical
│   └── آکوستیک  Acoustic
├── آمپلی فایر  Amplifier
│   └── (empty box)
└── تجهیزات جانبی  Accessory equipment / peripherals
    ├── افکت و یونیت  Effects and units
    └── دیلدو  (term unclear, see §6)
```

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
│   │       └── سوزن و کلاهک..  Needle and cap… (label truncated in the PDF)
│   └── سیستم تهویه  Ventilation system
│       └── تمیزکاری و بررسی  Cleaning and inspection
├── تامین منابع  Resource supply
│   ├── ابزار پاشش  Spraying tools
│   │   └── پیستوله  Spray gun
│   ├── آماده سازی چوب  Wood preparation   (no children)
│   ├── تهیه اقلام رنگ  Paint materials supply
│   │   └── رنگ , کیلر , سیلر , هاردنر موشتابا دسین
│   │       Paint, clear coat (کیلر), sealer, hardener, "موشتابا دسین" (see §6)
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

**[PDF]** A red arrow runs from "ابزار پاشش" (Spraying tools, under Resource
supply) to "پیستوله" (Spray gun, under Equipment maintenance). It is the only
cross-branch link in the PDF.

**[Interpretation]** The spray gun that Resource supply provides is the same
physical asset that Equipment maintenance services. The same equipment is seen
from two sides: procurement and upkeep.

**[PDF]** A small white hand-drawn tick or curved arrow sits between "تهیه
اقلام رنگ" and its child box. Its meaning is unknown (see §6).

### 1.3 Customer Communication (ارتباط با مشتری)

**[PDF]**

```
ارتباط با مشتری  Customer Communication
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

**[Interpretation]** Rubika and Bale are Iranian messaging platforms. The
business serves customers in Iran and expects them on these channels.

---

## 2. Departments

| Department | Status in PDF | Notes |
|---|---|---|
| Repair and Service | Scope defined (what is repaired) | No process, roles, or pricing shown |
| Paint Department | Equipment, consumables, safety defined | The only department with operational detail |
| Customer Communication | Channels defined | **[Interpretation]** A function, not necessarily a staffed department |
| Sales | Name only | |
| Management | Name only | A second "Management" also appears under the Paint Department |
| Accounting | Name only | |
| Carpentry | Name only | |
| CNC | Name only | |
| Purchasing | Name only | Overlaps with Paint "Resource supply" (see §6) |

**[Assumption]** `CLAUDE.md` describes the business as a guitar workshop
covering manufacturing, sales, and repairs. The PDF has no box called
"manufacturing". Carpentry, CNC, and Paint are the usual stages of building a
guitar body and neck, so manufacturing is assumed to be carried out by these
three departments together.

**[PDF]** Missing from the PDF entirely: warehouse/inventory, assembly and
setup, electronics/wiring, quality control, HR, and delivery/shipping.
Whether these exist in the business is unknown.

---

## 3. Products and services

| Item | Basis |
|---|---|
| Repair and service of electric, bass, classical, and acoustic guitars | **[PDF]** |
| Repair and service of amplifiers (types not given) | **[PDF]** |
| Repair and service of accessory equipment: effects units and "دیلدو" | **[PDF]** |
| Painting/finishing of wood (wood preparation, paint, clear coat, sealer, polish) | **[PDF]**, as Paint Department resources |
| Woodworking and CNC machining | **[PDF]**, names only |
| Guitars built and sold by the business | **[Assumption]** from `CLAUDE.md` and the Carpentry/CNC/Paint departments |
| Sale of accessories, amps, or parts | **[Assumption]**, not shown |
| Paint/refinish offered to customers as a service (as opposed to only internal production) | Unknown |

---

## 4. Requirements

IDs are stable; refer to them in issues and commits. "Basis" names the PDF node
that a requirement comes from. Requirements marked **[Recommendation]** are
proposals and are not approved for implementation.

### 4.1 Organisation

| ID | Requirement | Basis |
|---|---|---|
| BR-ORG-1 | The system represents these departments: Repair and Service, Paint, Customer Communication, Sales, Management, Accounting, Carpentry, CNC, Purchasing. | **[PDF]** the nine green boxes |
| BR-ORG-2 | Departments can have sub-units: Paint has Equipment maintenance, Resource supply, and Management. | **[PDF]** §1.2 |
| BR-ORG-3 | The department structure must be easy to change: six departments are still placeholders. | **[Interpretation]** of the empty boxes |

Note: the existing User Manager already supports a department tree with
`parent_id`, and teams per department (`CLAUDE.md`). BR-ORG-1 to BR-ORG-3 can
be met with data rather than code.

### 4.2 Repair and Service

| ID | Requirement | Basis |
|---|---|---|
| BR-REP-1 | Classify repair items into Guitar, Amplifier, and Accessory equipment. | **[PDF]** §1.1 |
| BR-REP-2 | Classify guitars as Electric, Bass, Classical, or Acoustic. | **[PDF]** §1.1 |
| BR-REP-3 | Classify accessories as Effects/units or "دیلدو" (pending clarification). | **[PDF]** §1.1 |
| BR-REP-4 | Allow amplifier sub-types to be added later. | **[Interpretation]** of the empty box |
| BR-REP-5 | Record each repair job against a customer and the item received, with status, diagnosis, work done, parts used, cost, and dates. | **[Assumption]** standard repair management |
| BR-REP-6 | Notify the customer when the status changes, on their preferred channel. | **[Recommendation]**, links to §4.4 |

### 4.3 Paint Department

| ID | Requirement | Basis |
|---|---|---|
| BR-PNT-1 | Keep a register of paint-shop equipment: compressor, spray guns, ventilation system. | **[PDF]** §1.2 |
| BR-PNT-2 | Define maintenance tasks per equipment type: compressor oil, belt, air filter, and fittings checks; spray gun cleaning and inspection (cup washing, needle and cap); ventilation cleaning and inspection. | **[PDF]** §1.2 |
| BR-PNT-3 | Record when each maintenance task was done and by whom. | **[Assumption]** |
| BR-PNT-4 | Schedule maintenance tasks at intervals (daily, per use, hours, ...) and flag overdue ones. | **[Recommendation]**: intervals are not in the PDF |
| BR-PNT-5 | Track paint-shop supplies by category: spraying tools, wood preparation, paint materials (paint, clear coat, sealer, hardener, ...), finishing tools (sandpaper, polish, pads), solvents (thinner), and safety equipment (gloves, masks, goggles). | **[PDF]** §1.2 |
| BR-PNT-6 | A spray gun is both a supplied item and a maintained asset; the two views must refer to the same record. | **[PDF]** red arrow, **[Interpretation]** of its meaning |
| BR-PNT-7 | Track stock levels of consumables and raise a purchase request when stock falls below a minimum. | **[Recommendation]** |
| BR-PNT-8 | Track issue of safety equipment (PPE) to staff. | **[Recommendation]**: the PDF lists PPE only as supplies |
| BR-PNT-9 | Record batch and expiry for paints, hardeners, and solvents, which are hazardous and time-limited. | **[Recommendation]** |

### 4.4 Customer Communication

| ID | Requirement | Basis |
|---|---|---|
| BR-CUS-1 | Record customer contact channels: in person; phone call; SMS; website; Telegram; Instagram; Rubika; Bale. | **[PDF]** §1.3 |
| BR-CUS-2 | Record which channel each customer interaction came through. | **[Interpretation]**: the reason for listing channels |
| BR-CUS-3 | Store per-customer contact handles (phone, Telegram ID, Instagram handle, ...) and a preferred channel. | **[Recommendation]** |
| BR-CUS-4 | Report enquiries and orders by channel. | **[Recommendation]** |
| BR-CUS-5 | Integrations that send messages through these platforms (SMS gateway, Telegram/Bale bots). | **[Recommendation]**, later phase; needs approval |

### 4.5 Sales, Purchasing, Accounting, Management, Carpentry, CNC

**[PDF]** Names only. No requirements can be derived from the PDF.

**[Recommendation]** Minimum scope to confirm with the business:

| ID | Area | Proposed scope |
|---|---|---|
| BR-SAL-1 | Sales | Customers, quotes, sales orders, invoices for guitars, accessories, and repair jobs. |
| BR-PUR-1 | Purchasing | Suppliers, purchase requests from departments (Paint first), purchase orders, goods receipt. |
| BR-ACC-1 | Accounting | Record invoices and payments; export to external accounting software rather than building a general ledger. |
| BR-MGT-1 | Management | Dashboards and approvals across departments. |
| BR-MFG-1 | Carpentry, CNC | Production orders that move through Carpentry → CNC → Paint, with materials consumed and time spent per stage. |

---

## 5. Missing information

Questions for the business, in priority order:

1. **Manufacturing.** Does the business build guitars? If so, what is the
   route through Carpentry, CNC, Paint, and any assembly/setup step? Built to
   order, to stock, or both?
2. **Repair process.** Intake, diagnosis, quote and approval, work,
   handover. Who does each step? Are customer approvals required before work?
   Are there warranties?
3. **Amplifier repairs.** Which types? The box under Amplifier is empty.
4. **Placeholder departments.** What do Sales, Management, Accounting,
   Carpentry, CNC, and Purchasing do? Who works there?
5. **Purchasing vs Resource supply.** Does the Paint Department buy its own
   supplies, or request them from Purchasing?
6. **Paint Management.** What does the "Management" box under the Paint
   Department cover: scheduling, staff, quality?
7. **Inventory.** Is there a central warehouse? Which items are stocked,
   and in what units?
8. **Maintenance intervals.** How often is each equipment task done? Is a
   log kept today?
9. **Customers.** Retail only, or also dealers and wholesale? What customer
   data is collected?
10. **Money.** Currency, tax/VAT rules, invoicing requirements, and the
    accounting software in use.
11. **Painting as a service.** Is it sold to customers, or only part of
    production?
12. **Customer Communication.** Is it staffed, or just a list of channels used
    by Sales and Repair?

## 6. Ambiguities in the source

| Text in PDF | Location | Issue |
|---|---|---|
| دیلدو | Repair → Accessory equipment | Not a recognised guitar-equipment term. It may be a typo or shorthand. Confirm what is meant before it appears in any user-facing list. |
| هاردنر موشتابا دسین | Paint → Paint materials supply | "Hardener" is clear. "موشتابا دسین" is not a recognised term: possibly a brand or product name, or a typo. |
| کیلر | Paint → Paint materials supply | Read as clear coat/lacquer, as used in Persian wood finishing. Confirm. |
| سوزن و کلاهک.. | Paint → Spray gun → Cleaning | Truncated in the PDF. Most likely "needle and air cap" (سوزن و کلاهک هوا). Confirm. |
| White tick | Next to تهیه اقلام رنگ | Could mean done, approved, or important. Unknown. |
| Empty boxes | Amplifier; Paint → Management; departments 4 to 9 | Read as placeholders. |
| "Management" twice | Top level, and under Paint | Unclear whether Paint Management reports to company Management. |
| آماده سازی چوب | Paint → Resource supply | Wood preparation sits under Paint, not Carpentry. Unclear who prepares wood for finishing. |
| No links between departments | Whole page | The PDF gives no reporting lines and no hand-offs (for example, Carpentry → Paint). |
