# Domain Model

Source: `morix-comp-1.pdf` in the repository root. Labels **[PDF]**,
**[Interpretation]**, **[Assumption]**, and **[Recommendation]** have the
meanings defined in [BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md#how-to-read-this-document).
Processes are in [WORKFLOWS.md](WORKFLOWS.md).

This document describes the business domain. It is **not** a database schema
and approves no modules. Each new business module still needs explicit
approval (`CLAUDE.md`), and its design should be checked against this document.

## 1. Glossary

Persian terms exactly as written in the PDF, with the English term to use in code
and the API.

| Persian (PDF) | English term | Kind |
|---|---|---|
| تعمیر و سرویس | Repair and Service | Department |
| بخش رنگ | Paint Department | Department |
| ارتباط با مشتری | Customer Communication | Department / function |
| فروش | Sales | Department |
| مدیریت | Management | Department; also a Paint sub-unit |
| حسابداری | Accounting | Department |
| نجاری | Carpentry | Department |
| CNC | CNC | Department |
| خرید | Purchasing | Department |
| گیتار | Guitar | Repair item category |
| الکتریک / باس / کلاسیک / آکوستیک | Electric / Bass / Classical / Acoustic | Guitar type |
| آمپلی فایر | Amplifier | Repair item category |
| تجهیزات جانبی | Accessory equipment | Repair item category |
| افکت و یونیت | Effects and units | Accessory type |
| دیلدو | (unclear, to be confirmed) | Accessory type |
| نگهداری تجهیزات | Equipment maintenance | Paint sub-unit |
| تامین منابع | Resource supply | Paint sub-unit |
| کمپرسور | Compressor | Equipment |
| پیستوله | Spray gun | Equipment and supplied tool |
| سیستم تهویه | Ventilation system | Equipment |
| بررسی روغن / بررسی تسمه / فیلتر هوا / بررسی اتصالات | Oil check / Belt check / Air filter / Fittings check | Maintenance task |
| تمیز کاری و بررسی | Cleaning and inspection | Maintenance task |
| شستشوی مخزن | Cup/tank washing | Maintenance task |
| سوزن و کلاهک.. | Needle and cap (truncated) | Maintenance task |
| ابزار پاشش | Spraying tools | Supply category |
| آماده سازی چوب | Wood preparation | Supply category |
| تهیه اقلام رنگ | Paint materials | Supply category |
| رنگ / کیلر / سیلر / هاردنر | Paint / Clear coat / Sealer / Hardener | Paint material |
| ابزار پرداخت | Finishing tools | Supply category |
| سنباده / پولیش و پد پولیش | Sandpaper / Polish and polishing pads | Finishing tool |
| حلال ها / تینر | Solvents / Thinner | Supply category / item |
| ایمنی و محیط کار | Safety and work environment | Supply category |
| دستکش / ماسک / عینک مخصوص | Gloves / Mask / Safety goggles | PPE item |
| حضوری / تلفنی / آنلاین | In person / Phone / Online | Channel group |
| زنگ / پیامک | Call / SMS | Phone channel |
| سایت / تلگرام / اینستاگرام / روبیکا / بله | Website / Telegram / Instagram / Rubika / Bale | Online channel |

## 2. Concepts evidenced by the PDF

**[PDF]** for the concepts and their parent-child structure. Their attributes are
**[Assumption]**.

```
Department ──< Department (sub-unit)              e.g. Paint ─< Equipment maintenance, Resource supply, Management

RepairItemCategory ──< RepairItemType              Guitar ─< Electric, Bass, Classical, Acoustic
                                                   Amplifier ─< (none yet)
                                                   Accessory equipment ─< Effects and units, دیلدو

EquipmentType ──< MaintenanceTask (──< sub-task)   Compressor ─< oil, belt, air filter, fittings
                                                   Spray gun ─< cleaning & inspection ─< cup, needle & cap
                                                   Ventilation ─< cleaning & inspection

SupplyCategory ──< SupplyItem                      Paint materials ─< paint, clear coat, sealer, hardener
                                                   Solvents ─< thinner; Safety ─< gloves, mask, goggles; ...

SupplyItem "spray gun"  ────────►  EquipmentType "spray gun"     (the red arrow: same thing)

ChannelGroup ──< Channel                           Phone ─< call, SMS; Online ─< website, Telegram, ...
```

Observations:

- **[PDF]** Every structure is a tree. The spray-gun arrow is the only link
  between trees.
- **[Interpretation]** Maintenance tasks can have sub-tasks: "Cleaning and
  inspection" has two children. A checklist with nested steps fits.
- **[Interpretation]** Item categories are lists the business expects to grow.
  The empty boxes show this. They are reference data, not code.

## 3. Proposed domain model

**[Recommendation]** Everything in this section. It combines the PDF concepts
with standard ERP entities a workshop needs. Names are proposals.

### 3.1 Shared (Core / User Manager, already implemented)

| Entity | Status | Use for this domain |
|---|---|---|
| Department (tree via `parent_id`) | Implemented | Seed the nine PDF departments and the Paint sub-units as data. |
| Team | Implemented | Crews within a department, for example spray booth staff. |
| User | Implemented | Staff; `primary department` matches the PDF departments. |
| Role / permission | Implemented | Each module defines its own permissions. Department-scoped permissions do not exist yet. They will be needed if, for example, Paint staff may only see Paint data. |
| AuditEvent | Implemented | Record admin and security actions in every module. |

### 3.2 Parties

| Entity | Key attributes | Basis |
|---|---|---|
| Customer | name, phone, email (optional), notes, preferred channel | **[Assumption]** |
| CustomerContact | customer, channel, handle (phone number, Telegram ID, Instagram handle, ...) | **[PDF]** channels; handles **[Assumption]** |
| Channel | code, name, group (in person / phone / online) | **[PDF]** §1.3 |
| Supplier | name, contacts, items supplied | **[Assumption]** |

### 3.3 Catalogue and inventory

| Entity | Key attributes | Basis |
|---|---|---|
| ItemCategory (tree) | name, parent | **[PDF]** supply categories |
| Item | SKU, name, category, unit of measure, tracked in stock (yes/no), min stock, hazardous flag | **[Assumption]** |
| StockLocation | warehouse, paint store, workshop | **[Assumption]** |
| StockMovement | item, location, quantity (+/-), reason (receipt, issue to job, adjustment), reference | **[Assumption]** |
| Lot | item, batch number, expiry; for paints, hardeners, and solvents | **[Recommendation]** |

**[Recommendation]** Use one Item master for paint supplies, repair parts, and
products for sale, separated by category. Do not create one table per PDF
category: the categories are data and will change.

### 3.4 Equipment and maintenance

| Entity | Key attributes | Basis |
|---|---|---|
| EquipmentType | name (compressor, spray gun, ventilation, ...) | **[PDF]** |
| Equipment | type, department, name/asset tag, serial, status (in use / out of service / retired), source Item if bought | **[Assumption]**; the Item link follows from the red arrow |
| MaintenanceTaskTemplate (tree) | equipment type, name, parent task, interval | **[PDF]** tasks; interval **[Assumption]** |
| MaintenanceRecord | equipment, task, done by, done at, result (OK / fixed / problem), notes | **[Assumption]** |

### 3.5 Repair and service

| Entity | Key attributes | Basis |
|---|---|---|
| RepairItemType (tree) | Guitar → Electric, ...; Amplifier; Accessory → Effects/units, ... | **[PDF]** |
| ServiceItem | customer, item type, brand, model, serial, description | **[Assumption]**: the customer-owned instrument or device |
| RepairOrder | number, customer, service item, intake channel, reported problem, condition at intake, status, assigned technician, dates (received, promised, completed, collected) | **[Assumption]** |
| RepairLine | repair order, labour or part (Item), quantity, price | **[Assumption]** |
| RepairStatus | received → diagnosing → awaiting approval → approved / declined → in progress → ready → collected | **[Assumption]** |

### 3.6 Manufacturing

| Entity | Key attributes | Basis |
|---|---|---|
| Product / Model | name, guitar type (Electric / Bass / Classical / Acoustic), bill of materials | **[Assumption]**; guitar types reused from the PDF |
| ProductionOrder | product, quantity, status, customer/sales order (if built to order) | **[Assumption]** |
| ProductionStep | production order, department (Carpentry, CNC, Paint, ...), sequence, status, time spent | **[Assumption]**; departments **[PDF]** |
| MaterialIssue | step, item, quantity | **[Assumption]**: a StockMovement with a production reference |

### 3.7 Sales, purchasing, accounting

| Entity | Basis |
|---|---|
| Quote, SalesOrder, Invoice, Payment | **[Assumption]** |
| PurchaseRequest (from a department), PurchaseOrder, GoodsReceipt, SupplierInvoice | **[Assumption]** |

**[Recommendation]** Keep accounting to invoices, payments, and an export to
the accounting software the business uses. A general ledger is out of scope
unless the business asks for it.

## 4. Key relationships

```
Customer ──< CustomerContact >── Channel
Customer ──< ServiceItem ──< RepairOrder ──< RepairLine >── Item
RepairOrder >── Channel (intake)
RepairOrder >── User (technician)
Item >── ItemCategory
Item ──< StockMovement >── StockLocation
Item ──< Equipment >── EquipmentType ──< MaintenanceTaskTemplate
Equipment ──< MaintenanceRecord >── MaintenanceTaskTemplate
Equipment >── Department
Product ──< ProductionOrder ──< ProductionStep >── Department
ProductionStep ──< MaterialIssue >── Item
Supplier ──< PurchaseOrder ──< GoodsReceipt ──► StockMovement
Department ──< PurchaseRequest
```

`A ──< B` means one A has many B; `B >── A` is the same read from B.

## 5. Suggested module boundaries

**[Recommendation]**, for discussion. Nothing here is approved. This follows the
module convention in `CLAUDE.md`.

| Module | Owns | Depends on |
|---|---|---|
| `customers` | Customer, CustomerContact, Channel | users |
| `inventory` | ItemCategory, Item, StockLocation, StockMovement, Lot | users |
| `maintenance` | EquipmentType, Equipment, task templates, records | inventory |
| `repairs` | RepairItemType, ServiceItem, RepairOrder | customers, inventory |
| `purchasing` | Supplier, PurchaseRequest, PurchaseOrder, GoodsReceipt | inventory |
| `sales` | Quote, SalesOrder, Invoice, Payment | customers, inventory |
| `production` | Product, ProductionOrder, ProductionStep | inventory, sales |

**[Recommendation]** Suggested order, given what the PDF actually details:
`customers` and `inventory` first, then `repairs` and `maintenance` (the two
areas with real content in the PDF). `production`, `sales`, and `purchasing`
follow once the business fills in the placeholder departments.

## 6. Modelling notes

- **[Recommendation]** Store category trees (repair item types, item
  categories, equipment types, channels) as reference data with `parent_id`,
  editable by admins. The PDF shows these lists are incomplete.
- **[Recommendation]** Use English codes in the database and API. Keep Persian
  display names as data, so the UI can be Persian later without schema changes.
- **[Recommendation]** Never delete records referenced by history (equipment,
  items, customers). Deactivate them, as User Manager already does for users.
- **[Assumption]** Currency is likely the Iranian rial or toman, given the
  messaging platforms. Store money as integer minor units or `Decimal`, never
  as float, and confirm the currency.
- Unclear terms ("دیلدو", "موشتابا دسین") must be confirmed before they are
  seeded as reference data. See
  [BUSINESS_REQUIREMENTS.md §6](BUSINESS_REQUIREMENTS.md#6-ambiguities-in-the-source).
