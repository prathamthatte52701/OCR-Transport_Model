// Single source of truth for the Transport receipt fields (matches backend extraction.py).
// `core` fields always render ("Not available" when blank); the rest are hidden when blank.
const F = (key, label, core = false) => ({ key, label, core })

export const RECEIPT_FIELDS = [
  F('operatorName', 'Operator Name', true),
  F('operatorGstin', 'Operator GSTIN', true),
  F('receiptNumber', 'Receipt Number', true),
  F('date', 'Date', true),
  F('toPlace', 'To Place', true),
  F('consigneeName', 'Consignee Name', true),
  F('consignorName', 'Consignor Name', true),
  F('packageCount', 'Package Count', true),
  F('paymentMode', 'Payment Mode', true),
  F('totalAmount', 'Total Amount', true),
  F('preparedBy', 'Prepared By', true),
  F('time', 'Time'),
  F('fromPlace', 'From Place'),
  F('deliveryAddress', 'Delivery Address'),
  F('consignorGstin', 'Consignor GSTIN'),
  F('consignorPhone', 'Consignor Phone'),
  F('consigneeGstin', 'Consignee GSTIN'),
  F('consigneePhone', 'Consignee Phone'),
  F('packageDescription', 'Package Description'),
  F('freight', 'Freight'),
  F('deliveryCharge', 'Delivery Charge'),
  F('demurrage', 'Demurrage'),
  F('sgst', 'SGST'),
  F('cgst', 'CGST'),
  F('igst', 'IGST'),
  F('amountInWords', 'Amount in Words'),
  F('remark', 'Remark'),
]

// Every key the UI copies off a document: the fields plus their review/auto-corrected flags.
const STATE_KEYS = RECEIPT_FIELDS.flatMap(({ key }) => [key, `${key}NeedsReview`, `${key}AutoCorrected`])

export function pickReceipt(doc) {
  return { ...Object.fromEntries(STATE_KEYS.map((k) => [k, doc[k]])), warnings: doc.warnings }
}

// [{key,label,core,value,needsReview}] for a document (or bulk row); blank optional fields dropped.
export function receiptFieldsFor(doc) {
  return RECEIPT_FIELDS
    .map(({ key, label, core }) => ({ key, label, core, value: doc[key], needsReview: !!doc[`${key}NeedsReview`] }))
    .filter((f) => f.core || String(f.value ?? '').trim())
}
