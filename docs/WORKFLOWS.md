# Workflows

Source: `morix-comp-1.pdf` in the repository root. Labels **[PDF]**,
**[Interpretation]**, **[Assumption]**, and **[Recommendation]** have the
meanings defined in [BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md#how-to-read-this-document).
Entities are described in [DOMAIN_MODEL.md](DOMAIN_MODEL.md).

## Summary

**[PDF]** The PDF is a hierarchy of departments, categories, and items. It
contains **no process flows**: no sequences, decisions, hand-offs, roles, or
timings.

The only process content in it is a set of maintenance checklists (§1)
and the categories of supplies the Paint Department must obtain (§2).

Everything in §3 onwards is **[Assumption]**: common ERP workflows for a
guitar workshop, written down so they can be reviewed with the business. None of
them is approved for implementation.

---

## 1. Paint equipment maintenance

**[PDF]** Tasks per equipment type. The PDF gives no order, frequency, or
responsible person.

| Equipment | Task (Persian) | Task (English) |
|---|---|---|
| Compressor (کمپرسور) | بررسی روغن | Check oil |
| | بررسی تسمه | Check belt |
| | فیلتر هوا | Air filter (check/clean/replace not stated) |
| | بررسی اتصالات | Check connections and fittings |
| Spray gun (پیستوله) | تمیز کاری و بررسی → شستشوی مخزن | Clean and inspect: wash the cup/tank |
| | تمیز کاری و بررسی → سوزن و کلاهک.. | Clean and inspect: needle and (air) cap |
| Ventilation system (سیستم تهویه) | تمیزکاری و بررسی | Clean and inspect |

**[Assumption]** Workflow:

1. Each piece of equipment has a maintenance plan: tasks and an interval.
2. The system lists tasks that are due or overdue.
3. A Paint Department worker does the task and records the result: OK,
   fixed, or a problem found, with notes.
4. A problem found raises a repair, or a purchase request for parts
   (filter, belt, needle).
5. Paint Management reviews overdue and failed tasks.

**[Recommendation]** Spray gun cleaning is normally done after every use or at
the end of each shift. Compressor checks are normally weekly or monthly, by run
hours. The real intervals must come from the business.

## 2. Paint shop supply

**[PDF]** Categories the Paint Department's "Resource supply" (تامین منابع)
covers: spraying tools (spray gun), wood preparation, paint materials (paint,
clear coat, sealer, hardener, ...), finishing tools (sandpaper, polish,
polishing pads), solvents (thinner), and safety equipment (gloves, mask,
goggles).

**[PDF]** The spray gun under Spraying tools is linked by an arrow to the spray
gun under Equipment maintenance.

**[Assumption]** Workflow:

1. Stock is kept per item, with a minimum level.
2. Using material for a job, or issuing PPE, reduces stock.
3. Stock below the minimum raises a purchase request.
4. Purchasing (خرید) orders from a supplier. **[Assumption]**: the PDF does
   not say whether Paint buys directly or through Purchasing.
5. On receipt, stock goes up. A spray gun, or other tool, is also added
   to the equipment register so it enters the maintenance plan (§1). This is
   the arrow in the PDF.

## 3. Repair and service (assumed)

**[PDF]** Only the scope is given: guitars (electric, bass, classical,
acoustic), amplifiers, accessory equipment (effects units, "دیلدو").

**[Assumption]** Typical repair-shop flow:

```
Intake ─► Diagnosis ─► Quote ─► Customer approval ─┬─► Repair ─► QC ─► Notify ─► Handover + payment
                                                    └─► Declined ─► Notify ─► Return item
```

1. **Intake.** The customer brings the item in person, or arranges it by phone
   or online (see §5). Record customer, item type (from the PDF categories),
   brand/model/serial, condition, accessories received (case, strap), reported
   problem, and contact channel. Give the customer a receipt or job number.
2. **Diagnosis.** A technician inspects and records findings, required work,
   and parts.
3. **Quote.** Labour and parts. Requires a price list. **[Assumption]**:
   no pricing data is in the PDF.
4. **Approval.** The customer approves or declines, on any channel. Record
   who approved, when, and how.
5. **Repair.** Do the work, use parts from stock, log time. Refinishing work
   may hand the item to the Paint Department.
6. **Quality check.** Setup, playing test, or amp test.
7. **Notify.** Tell the customer the item is ready, using their preferred
   channel.
8. **Handover.** Payment, invoice, and an optional warranty period.

**[Recommendation]** Track unclaimed items: the date notified, reminders,
and a storage policy.

## 4. Manufacturing (assumed)

**[PDF]** Carpentry (نجاری), CNC, and Paint Department (بخش رنگ) exist. No
flow between them is drawn, and no manufacturing department is named.

**[Assumption]** A typical guitar build route:

```
Order or plan ─► Material issue (wood) ─► CNC (body/neck shaping) ─► Carpentry (fitting, gluing, fretwork)
             ─► Wood preparation (sanding, filling) ─► Paint (seal, colour, clear, cure, polish)
             ─► Assembly/setup* ─► QC* ─► Finished stock or delivery to customer
```

`*` Steps that do not appear in the PDF at all.

The order of CNC and Carpentry varies by workshop and model. Confirm the real
route.

**[Recommendation]** A production order records the model, the route
(department steps), material issued per step, time per step, and status. The
Paint step consumes the materials listed in §2.

## 5. Customer communication (assumed)

**[PDF]** Channels: in person; phone (call, SMS); online (website, Telegram,
Instagram, Rubika, Bale).

**[Assumption]** Workflow:

1. An enquiry arrives on any channel.
2. Staff find or create the customer, and record the channel and handle.
3. The enquiry becomes a repair job (§3), a sales quote (§6), or is
   closed with a note.
4. Follow-ups use the customer's preferred channel.

**[Recommendation]** Phase 1 records channels manually. Sending messages
through SMS or bots (Telegram, Bale) is a later integration.

## 6. Sales, purchasing, accounting (assumed)

**[PDF]** Names only.

**[Assumption]** Standard flows:

- **Sales:** quote → sales order → (production order or stock reservation) →
  delivery → invoice → payment.
- **Purchasing:** purchase request (from a department) → approval → purchase
  order → goods receipt → supplier invoice → payment.
- **Accounting:** receives sales and supplier invoices and payments; reports
  and tax. **[Recommendation]**: integrate with existing accounting software
  rather than build a general ledger.
- **Management:** approvals above set limits; reports across departments.

## 7. Cross-department hand-offs to confirm

None of these are in the PDF. Each is an **[Assumption]** to verify:

| From | To | What |
|---|---|---|
| Customer Communication | Repair and Service / Sales | Enquiries become jobs or quotes |
| Repair and Service | Paint Department | Refinishing work |
| Carpentry / CNC | Paint Department | Bodies and necks ready for finishing |
| Paint Department | Purchasing | Supply requests |
| Purchasing | Accounting | Supplier invoices |
| Sales / Repair | Accounting | Customer invoices and payments |
| All departments | Management | Reports, approvals |
