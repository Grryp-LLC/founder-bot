"""Privacy gate for anything that lands on a shareable Launch Board card or caption.

Enforced, not advisory. The renderer refuses to render (exit 2) if any of these appear:
  * email addresses, URLs, phone numbers
  * EINs / SSNs / tax IDs (NN-NNNNNNN, NNN-NN-NNNN) and any run of 4+ digits that is not a year
  * dollar amounts (budget, revenue, fees stay private)
  * street addresses (a number followed by a street word)
  * names on the owner's deny-list (their own name, co-founders, family)
"""
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
URL = re.compile(r"(https?://\S+|www\.\S+|\b[\w-]+\.(com|net|org|io|co|shop|store|app)\b)", re.I)
PHONE = re.compile(r"\+?\d[\d\s().-]{8,}\d")
TAXID = re.compile(r"\b\d{2}-\d{7}\b|\b\d{3}-\d{2}-\d{4}\b")
MONEY = re.compile(r"\$\s?\d|\b\d+(\.\d+)?\s?(usd|dollars|bucks|k)\b", re.I)
LONGNUM = re.compile(r"\d{4,}")
STREET = re.compile(r"\b\d{1,5}\s+(\w+\s){0,3}(st|street|ave|avenue|rd|road|blvd|lane|ln|dr|drive|hwy|suite|ste)\b\.?", re.I)


def lint(text: str, deny_names=()) -> list:
    probs = []
    for rx, label in ((EMAIL, "email address"), (URL, "url or domain"), (TAXID, "tax id"),
                      (PHONE, "phone number"), (MONEY, "dollar amount"), (STREET, "street address")):
        if rx.search(text):
            probs.append(label)
    for m in LONGNUM.finditer(text):
        if not (1990 <= int(m.group(0)) <= 2100):
            probs.append("long number " + m.group(0))
    for n in deny_names or ():
        if n and len(n.strip()) >= 2 and re.search(r"\b" + re.escape(n.strip()) + r"\b", text, re.I):
            probs.append("denied name")
    return sorted(set(probs))


def spec_text(spec: dict) -> str:
    parts = [str(spec.get(k, "")) for k in ("mission", "launch_label", "week_label", "caption")]
    parts += [str(x) for x in spec.get("next", [])]
    parts += [str(s.get("label", "")) for s in spec.get("stages", [])]
    return "\n".join(parts)
