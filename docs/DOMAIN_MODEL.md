# Domain Model

Source: `morix-erp.pdf` in the repository root. Labels **[PDF]** and
**[Interpretation]** are defined in
[BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md#how-to-read-this-document).
Process elements are in [WORKFLOWS.md](WORKFLOWS.md).

This document records the concepts and relationships the PDF shows. It is
**not** a database schema, and it proposes no entities, attributes, or
modules. Each new business module still needs explicit approval (`CLAUDE.md`),
and its design must be checked against this document. Anything added beyond
the PDF must be labelled and confirmed with the business first.

## 1. Glossary

Terms exactly as written in the PDF, with the English term to use in code and
the API.

| PDF text | English term | Where |
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
| الکتریک | Electric | Guitar type |
| باس (Repair) / بیس (Production) | Bass | Guitar type |
| کلاسیک | Classical | Guitar type (Repair only) |
| آکوستیک | Acoustic | Guitar type (Repair only) |
| 4 / 5 / 6 / 7 / 8 string | 4- to 8-string | Guitar variant (Production) |
| آمپلی فایر | Amplifier | Repair, Production, Warranty |
| RG10 | RG10 | Amplifier (Production) |
| پری آمپ گیتار | Guitar preamp | Production, Warranty |
| گیتار بیس / گیتار الکتریک | Bass guitar / Electric guitar | Preamp target |
| passive / active | Passive / Active | Preamp variant |
| بارتولینی | Bartolini | Under passive bass preamp |
| قطعات گیتار / لوازم جانبی | Guitar parts / Accessories | Production, Warranty |
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
| رنگ / کیلر / سیلر / هاردنر | Paint / Clear coat / Sealer / Hardener | Paint material |
| ابزار پرداخت | Finishing tools | Supply category |
| سنباده / پولیش و پد پولیش | Sandpaper / Polish and polishing pads | Finishing tool |
| حلال ها / تینر | Solvents / Thinner | Supply category / item |
| ایمنی و محیط کار | Safety and work environment | Supply category |
| دستکش / ماسک / عینک مخصوص | Gloves / Mask / Safety goggles | Safety item |
| شخص ثالث / حضوری / تلفنی / آنلاین | Third party / In person / Phone / Online | Channel group |
| زنگ / پیامک | Call / SMS | Phone channel |
| سایت / تلگرام / اینستاگرام / روبیکا / بله | Website / Telegram / Instagram / Rubika / Bale | Online channel |

## 2. Concepts shown in the PDF

**[PDF]** Every structure is a tree under one area:

```
Area ──< sub-unit                       Paint ─< Equipment maintenance, Resource supply, Management

Production category ──< variant         Guitar ─< Electric ─< 6/7/8 string
                                                ─< Bass ─< 4/5/6 string
                                        Amplifier ─< RG10
                                        Guitar preamp ─< Bass guitar ─< passive ─< Bartolini
                                                      ─< Electric guitar ─< active
                                        Guitar parts / Accessories (no children)

Warranty ──< covered category           Guitar parts / Accessories, Guitar, Amplifier, Guitar preamp

Repair item category ──< type           Guitar ─< Electric, Bass, Classical, Acoustic
                                        Amplifier (no children)
                                        Accessory equipment ─< Effects and units

Equipment ──< maintenance task ──< sub-task
                                        Compressor ─< oil, belt, air filter, fittings
                                        Spray gun ─< cleaning & inspection ─< cup washing, needle & air cap
                                        Ventilation ─< cleaning & inspection

Supply category ──< item                Paint materials ─< paint, clear coat, sealer, hardener, ...
                                        Solvents ─< thinner; Safety ─< gloves, mask, goggles; ...

Channel group ──< channel               Phone ─< call, SMS; Online ─< website, Telegram, Instagram, Rubika, Bale
                                        Third party, In person (no children)
```

## 3. Relationships shown in the PDF

| Relationship | Source |
|---|---|
| Each of the six guitar services applies to each of the four repair guitar types (many-to-many, every pair present). | **[PDF]** arrows; checked against vector paths |
| Supply item "Spray gun" and Equipment "Spray gun" refer to the same thing. | **[PDF]** arrow; **[Interpretation]** of its meaning |
| Warranty and Production use the same four category names. | **[PDF]** labels. A link between them is not drawn. |
| Repair and Production both use Guitar and Amplifier. Repair lists classical and acoustic guitars, Production does not. Production lists preamps and parts/accessories, Repair does not. | **[PDF]** labels |

**[PDF]** No other relationships are drawn: none between areas, none between
staff and areas, and none between customers and anything.

## 4. Fit with what is already implemented

These are facts about the existing code, not about the business:

- User Manager has a department tree (`parent_id`) and teams. It can hold the
  eleven areas and the Paint sub-units as data.
- User Manager has roles and permissions; department-scoped permissions are
  not implemented.
- AuditEvent is available to every module.

## 5. Modelling constraints from the PDF

- **[Interpretation]** Several lists are visibly incomplete: empty boxes,
  and categories with no children. Store such lists as data that can grow,
  not as fixed code enums.
- Terms listed as ambiguous in
  [BUSINESS_REQUIREMENTS.md §6](BUSINESS_REQUIREMENTS.md#6-ambiguities-in-the-source)
  must be confirmed before they are seeded as reference data.
