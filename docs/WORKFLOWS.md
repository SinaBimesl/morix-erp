# Workflows

Source: `morix-erp.pdf` in the repository root, plus the owner-confirmed
clarifications C1–C7. Labels **[PDF]**, **[Owner]**, and **[Interpretation]**
are defined in
[BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md#how-to-read-this-document),
and the clarifications are listed in
[§2 there](BUSINESS_REQUIREMENTS.md#2-owner-confirmed-clarifications).
Concepts are in [DOMAIN_MODEL.md](DOMAIN_MODEL.md).

## Summary

**[PDF]** The PDF is a set of hierarchies. It contains **no process flows**:
no sequences, decisions, statuses, hand-offs, roles, or timings. The owner's
clarifications define terms and scope; they add no process flows either.

This document lists only the process elements the PDF shows. Each section ends
with the questions that must be answered before the workflow can be designed.
No workflow here is approved, and none is assumed.

**[Owner]** C7: Every workflow runs inside the workshop. MorixERP is used by
workshop managers; customers never act in the system themselves.

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

**[Owner]** C5: Clear coat, hardener, and sealer are materials used in the
painting and finishing process.

Questions: Does Paint buy directly or through Purchasing (خرید)? Is stock
kept, and with what minimum levels? Is safety equipment issued to named staff?
What is "موشتابا دسین"?

## 3. Repair and service

**[PDF]**
- **Items accepted:** guitars (electric, Bass Guitar, classical, acoustic),
  amplifiers, and accessory equipment (effects and units).
- **Services offered for guitars:** instrument upgrade, general setup, fret
  levelling, electronics repair and upgrade, refret, paint/finish repair.
  Each service applies to all four guitar types.

**[Owner]** C6: Classical and acoustic guitars are not manufactured, but they
may be included in repair services. C1: "Bass Guitar" covers both باس and
بیس.

Questions: What are the intake, diagnosis, quote, approval, work, and handover
steps? Does paint/finish repair go to the Paint Department? Which services
exist for amplifiers and effects units? How are services priced? How does a
repair relate to Warranty (§5)?

## 4. Production

**[PDF]** Product categories and variants: Guitar Parts and Accessories;
electric guitars (6, 7, 8 string); Bass Guitar (4, 5, 6 string); amplifier
RG10; guitar preamps (Bass Guitar: passive, Bartolini; electric guitar:
active).

**[Owner]**
- C6: Production is limited to electric guitars and bass guitars. Classical
  and acoustic guitars are not manufactured.
- C2: Guitar Parts and Accessories is one category.
- C3: Bartolini is a type of preamp.
- C4: RG10 is an amplifier model.

**[PDF]** Carpentry (نجاری), CNC, and the Paint Department appear as separate
areas. No link is drawn between them and Production.

Questions: The PDF also lists RG10, guitar preamps, and Guitar Parts and
Accessories under Production; are they manufactured, given C6? Which areas
take part in building each product, and in what order? Built to order or to
stock? Are materials and time tracked per product?

## 5. Warranty

**[PDF]** Warranty covers four categories: Guitar Parts and Accessories (one
category, C2), guitar, amplifier, guitar preamp. These match the first level
of Production.

Questions: What are the terms and durations? How is a claim made, approved,
and fulfilled (repair, replacement, refund)? Is warranty work done by Repair
and Service?

## 6. Customer communication

**[PDF]** Channels: third party; in person; phone (call, SMS); online
(website, Telegram, Instagram, Rubika, Bale).

**[Owner]** C7: These channels are not interfaces to MorixERP. Customers have
no accounts and no portal.

Questions: Which enquiries arrive on which channels? Who handles them? Who is
the "third party"? Is the channel recorded per order or per customer?

## 7. Management, Accounting, Sales, CNC, Purchasing, Carpentry

**[PDF]** Names only. No process elements are shown.
