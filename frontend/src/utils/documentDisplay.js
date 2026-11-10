// "Number not read" = receiptNumber empty/whitespace/missing. Only a processed document can show it.
export function isNumberBlank(doc) {
  return !String(doc.receiptNumber ?? '').trim()
}

export function numberNotRead(doc) {
  return doc.uploadStatus === 'processed' && isNumberBlank(doc)
}

export function displayNumber(doc) {
  return doc.receiptNumber || '-'
}
