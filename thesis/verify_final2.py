# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
import re

OUTPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_润色版.docx"
doc = Document(OUTPUT)

# Get all text
all_text = ""
for para in doc.paragraphs:
    all_text += para.text + "\n"
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            all_text += cell.text + "\n"

print("=" * 60)
print("FINAL VERIFICATION REPORT")
print("=" * 60)

# Check forbidden words
yinci_count = all_text.count("因此")
benke_count = all_text.count("本课题")
print("\n1. FORBIDDEN WORD CHECK:")
print("   yinci(因此) count: " + str(yinci_count) + " (should be 0)")
print("   benke(本课题) count: " + str(benke_count) + " (should be 0)")

# Check key values (from Table 4.3)
print("\n2. KEY VALUES CHECK:")
key_values = ["1.65", "0.082", "-9.8%", "31.4%", "18.7%", "35"]
for val in key_values:
    count = all_text.count(val)
    status = "OK" if count > 0 else "MISSING"
    print("   " + val + ": " + str(count) + " occurrence(s) [" + status + "]")

# Check technical terms
print("\n3. TECHNICAL TERMS CHECK:")
terms = ["Transformer", "LSTM", "AdamW", "AlphaTransformer", "MAE", "RMSE", "return", "收益"]
for term in terms:
    count = all_text.count(term)
    status = "OK" if count > 0 else "MISSING"
    print("   " + term + ": " + str(count) + " occurrence(s) [" + status + "]")

# Check formula labels (2)-(6)
print("\n4. FORMULA LABELS CHECK:")
formula_labels = ["(1)", "(2)", "(3)", "(4)", "(5)", "(6)"]
for label in formula_labels:
    count = all_text.count(label)
    status = "OK" if count > 0 else "MISSING"
    print("   " + label + ": " + str(count) + " occurrence(s) [" + status + "]")

print("\n" + "=" * 60)
all_passed = (yinci_count == 0 and benke_count == 0 and 
              all(all_text.count(v) > 0 for v in key_values) and
              all(all_text.count(t) > 0 for t in ["Transformer", "LSTM", "AlphaTransformer"]))
result = "ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED"
print("OVERALL: " + result)
print("=" * 60)
