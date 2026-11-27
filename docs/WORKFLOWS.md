# Workflows

Source: `morix-erp.pdf` in the repository root. Labels **[PDF]** and
**[Interpretation]** are defined in
[BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md#how-to-read-this-document).
Concepts are in [DOMAIN_MODEL.md](DOMAIN_MODEL.md).

## Summary

**[PDF]** The PDF is a set of hierarchies. It contains **no process flows**:
no sequences, decisions, statuses, hand-offs, roles, or timings.

This document lists only the process elements the PDF does show. Each section
ends with the questions that must be answered before the workflow can be
designed. No workflow here is approved, and none is assumed.

---

## 1. Paint equipment maintenance

**[PDF]** Tasks per equipment type. No order, frequency, or responsible
person is given.

| Equipment | Task (Persian) | Task (English) |
|---|---|---|
| Compressor (کمپرسور) | بررسی روغن | Check oil |
| | بررسی تسمه | Check belt |
| | فیلتر هوا | Air filter (check/clean/replace not stated) |
| | بررسی اتصالات | Check connections and fittings |
| Spray gun (پیستوله) | تمیز کاری و بررسی | Clean and inspect, made up of: |
| | └ شستشوی مخزن | Wash the cup/tank |
| | └ سوزن و کلاهک هوا | Needle and air cap |
| Ventilation system (سیستم تهویه) | تمیزکاری و بررسی | Clean and inspect |

**[PDF]** The spray gun is also listed under Resource supply → Spraying
tools, and an arrow links the two.

Questions: How often is each task done? Who does it? Is a record kept? What
happens when a check fails?

## 2. Paint shop supply

**[PDF]** Resource supply (تامین منابع) covers:
- spraying tools: spray gun;
- wood preparation: no items listed;
- paint materials: paint, clear coat, sealer, hardener, "موشتابا دسین";
- finishing tools: sandpaper, polish and polishing pads;
- solvents: thinner;
- safety and work environment: gloves, mask, safety goggles.

Questions: Does Paint buy directly or through Purchasing (خرید)? Is stock
kept, and with what minimum levels? Is safety equipment issued to named staff?

## 3. Repair and service

**[PDF]**
- **Items accepted:** guitars (electric, bass, classical, acoustic),
  amplifiers, and accessory equipment (effects and units).
- **Services offered for guitars:** instrument upgrade, general setup, fret
  levelling, electronics repair and upgrade, refret, paint/finish repair.
  Each service applies to all four guitar types.

Questions: What are the intake, diagnosis, quote, approval, work, and handover
steps? Does paint/finish repair go to the Paint Department? Which services
exist for amplifiers and effects units? How are services priced? How does a
repair relate to Warranty (§5)?

## 4. Production

**[PDF]** Product categories and variants: guitar parts/accessories; electric
guitars (6, 7, 8 string); bass guitars (4, 5, 6 string); amplifier RG10;
guitar preamps (bass: passive, Bartolini; electric: active).

**[PDF]** Carpentry (نجاری), CNC, and the Paint Department appear as separate
areas. No link is drawn between them and Production.

Questions: Which areas take part in building each product, and in what order?
Built to order or to stock? Are materials and time tracked per product?

## 5. Warranty

**[PDF]** Warranty covers four categories: guitar parts/accessories, guitar,
amplifier, guitar preamp. These match the first level of Production.

Questions: What are the terms and durations? How is a claim made, approved,
and fulfilled (repair, replacement, refund)? Is warranty work done by Repair
and Service?

## 6. Customer communication

**[PDF]** Channels: third party; in person; phone (call, SMS); online
(website, Telegram, Instagram, Rubika, Bale).

Questions: Which enquiries arrive on which channels? Who handles them? Who is
the "third party"? Is the channel recorded per order or per customer?

## 7. Management, Accounting, Sales, CNC, Purchasing, Carpentry

**[PDF]** Names only. No process elements are shown.
