# Domain Model

Source: `morix-erp.pdf` in the repository root, plus the owner-confirmed
clarifications C1–C7. Labels **[PDF]**, **[Owner]**, and **[Interpretation]**
are defined in
[BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md#how-to-read-this-document),
and the clarifications are listed in
[§2 there](BUSINESS_REQUIREMENTS.md#2-owner-confirmed-clarifications).
Process elements are in [WORKFLOWS.md](WORKFLOWS.md).

This document records the concepts and relationships the PDF shows, refined by
the owner's clarifications. It is **not** a database schema, and it proposes
no entities, attributes, or modules. Each new business module still needs
explicit approval (`CLAUDE.md`), and its design must be checked against this
document. Anything added beyond the PDF and the clarifications must be labelled
and confirmed with the business first.

## 1. Glossary

Terms exactly as written in the PDF, with the English term to use in code and
the API. A C-ID in the last column means the owner confirmed that entry.

| PDF text | English term | Where / meaning |
|---|---|---|
| تعمیر و سرویس | Repair and Service | Area |
| بخش رنگ | Paint Department | Area |
| ارتباط با مشتری | Customer Communication | Area |
| تولید | Production | Area |
| گارانتی | Warranty | Area |
| مدیریت | Management | Area; also a Paint sub-unit |
| حسابداری | Accounting | Area |
| فروش | Sales | Area |
| CNC | CNC | Area |
| خرید | Purchasing | Area |
| نجاری | Carpentry | Area |
| گیتار | Guitar | Repair, Production, Warranty |
| الکتریک | Electric | Guitar type; manufactured (C6) |
| باس (Repair) / بیس (Production) | **Bass Guitar** | Guitar type: one instrument, two spellings (C1); manufactured (C6) |
| کلاسیک | Classical | Guitar type; repair only, not manufactured (C6) |
| آکوستیک | Acoustic | Guitar type; repair only, not manufactured (C6) |
| 4 / 5 / 6 / 7 / 8 string | 4- to 8-string | Guitar variant (Production) |
| آمپلی فایر | Amplifier | Repair, Production, Warranty |
| RG10 | RG10 | Amplifier model (C4) |
| پری آمپ گیتار | Guitar preamp | Production, Warranty |
| گیتار بیس / گیتار الکتریک | Bass Guitar (C1) / Electric Guitar | Preamp target |
| passive / active | Passive / Active | Preamp variant |
| بارتولینی | Bartolini | A preamp type, not a brand or model (C3) |
| قطعات گیتار / لوازم جانبی | **Guitar Parts and Accessories** | One combined category (C2); Production, Warranty |
| تجهیزات جانبی | Accessory equipment | Repair |
| افکت و یونیت | Effects and units | Accessory equipment |
| ارتقا ساز | Instrument upgrade | Guitar service |
| رگلاژ عمومی | General setup | Guitar service |
| فرت لول | Fret levelling | Guitar service |
| تعمیر و ارتقا الکترونیک | Electronics repair and upgrade | Guitar service |
| ری فرت | Refret | Guitar service |
| ترمیم رنگ | Paint/finish repair | Guitar service |
| نگهداری تجهیزات | Equipment maintenance | Paint sub-unit |
| تامین منابع | Resource supply | Paint sub-unit |
| کمپرسور | Compressor | Equipment |
| پیستوله | Spray gun | Equipment; also a supply item |
| سیستم تهویه | Ventilation system | Equipment |
| بررسی روغن / بررسی تسمه / فیلتر هوا / بررسی اتصالات | Oil check / Belt check / Air filter / Fittings check | Maintenance task |
| تمیز کاری و بررسی | Cleaning and inspection | Maintenance task |
| شستشوی مخزن / سوزن و کلاهک هوا | Cup/tank washing / Needle and air cap | Maintenance sub-task |
| ابزار پاشش | Spraying tools | Supply category |
| آماده سازی چوب | Wood preparation | Supply category |
| تهیه اقلام رنگ | Paint materials | Supply category |
| رنگ | Paint | Paint material |
| کیلر / سیلر / هاردنر | Clear coat / Sealer / Hardener | Painting and finishing materials (C5) |
| موشتابا دسین | (unresolved) | Listed after hardener; meaning unknown |
| ابزار پرداخت | Finishing tools | Supply category |
| سنباده / پولیش و پد پولیش | Sandpaper / Polish and polishing pads | Finishing tool |
| حلال ها / تینر | Solvents / Thinner | Supply category / item |
| ایمنی و محیط کار | Safety and work environment | Supply category |
| دستکش / ماسک / عینک مخصوص | Gloves / Mask / Safety goggles | Safety item |
| شخص ثالث / حضوری / تلفنی / آنلاین | Third party / In person / Phone / Online | Channel group |
| زنگ / پیامک | Call / SMS | Phone channel |
| سایت / تلگرام / اینستاگرام / روبیکا / بله | Website / Telegram / Instagram / Rubika / Bale | Online channel |

## 2. Concepts shown in the PDF

**[PDF]** Every structure is a tree under one area. Owner clarifications are
marked by ID.

```
Area ──< sub-unit                       Paint ─< Equipment maintenance, Resource supply, Management

Production category ──< variant         Guitar ─< Electric ─< 6/7/8 string
                                                ─< Bass Guitar (C1) ─< 4/5/6 string
                                        Amplifier ─< RG10 (model, C4)
                                        Guitar preamp ─< Bass Guitar ─< passive ─< Bartolini (preamp type, C3)
                                                      ─< Electric Guitar ─< active
                                        Guitar Parts and Accessories (one category, C2; no children)

Warranty ──< covered category           Guitar Parts and Accessories, Guitar, Amplifier, Guitar preamp

Repair item category ──< type           Guitar ─< Electric, Bass Guitar, Classical, Acoustic
                                        Amplifier (no children)
                                        Accessory equipment ─< Effects and units

Equipment ──< maintenance task ──< sub-task
                                        Compressor ─< oil, belt, air filter, fittings
                                        Spray gun ─< cleaning & inspection ─< cup washing, needle & air cap
                                        Ventilation ─< cleaning & inspection

Supply category ──< item                Paint materials ─< paint, clear coat, sealer, hardener (C5), ...
                                        Solvents ─< thinner; Safety ─< gloves, mask, goggles; ...

Channel group ──< channel               Phone ─< call, SMS; Online ─< website, Telegram, Instagram, Rubika, Bale
                                        Third party, In person (no children)
```

## 3. Relationships

| Relationship | Source |
|---|---|
| Each of the six guitar services applies to each of the four repair guitar types (many-to-many, every pair present). | **[PDF]** arrows; checked against vector paths |
| Supply item "Spray gun" and Equipment "Spray gun" refer to the same thing. | **[PDF]** arrow; **[Interpretation]** of its meaning |
| Warranty and Production use the same four category names. | **[PDF]** labels. A link between them is not drawn. |
| Repair and Production both use Guitar and Amplifier. | **[PDF]** labels |
| Guitar types: Electric and Bass Guitar are manufactured; Classical and Acoustic are repair only. | **[PDF]** labels; **[Owner]** C6 |
| Production lists preamps and Guitar Parts and Accessories; Repair does not. | **[PDF]** labels |
| Bass Guitar in Repair (باس) and Bass Guitar in Production (بیس) are the same guitar type. | **[Owner]** C1 |

**[PDF]** No other relationships are drawn: none between areas, none between
staff and areas, and none between customers and anything.

## 4. System users

**[Owner]** C7: MorixERP is an internal workshop management system used by
workshop managers. Customers do not access it.

- Customers are not system users. There are no customer accounts, customer
  portals, or public interfaces.
- Whether staff other than workshop managers also log in is open
  ([BUSINESS_REQUIREMENTS.md §6](BUSINESS_REQUIREMENTS.md#6-open-questions),
  question 5).

## 5. Fit with what is already implemented

These are facts about the existing code, not about the business:

- User Manager has a department tree (`parent_id`) and teams. It can hold the
  eleven areas and the Paint sub-units as data.
- User Manager has roles and permissions; department-scoped permissions are
  not implemented.
- User Manager accounts are staff accounts. That matches C7, which rules out
  customer accounts.
- AuditEvent is available to every module.

## 6. Modelling constraints

- **[Interpretation]** Several lists are visibly incomplete: empty boxes,
  and categories with no children. Store such lists as data that can grow,
  not as fixed code enums.
- **[Owner]** Use one guitar type, "Bass Guitar", for both باس and بیس (C1),
  and one category, "Guitar Parts and Accessories" (C2).
- Terms still listed as ambiguous in
  [BUSINESS_REQUIREMENTS.md §7](BUSINESS_REQUIREMENTS.md#7-ambiguities-in-the-source)
  must be confirmed before they are seeded as reference data.
