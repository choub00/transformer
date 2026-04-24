import zipfile, os, re
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def is_black_color(c):
    return c is None or c.upper() in ('000000','AUTO','FF000000','00000000','')

def get_run_color(run):
    rPr = run.find(f'{W}rPr')
    if rPr is not None:
        color = rPr.find(f'{W}color')
        if color is not None:
            return color.get(f'{W}val')
    return None

def get_para_text(para):
    return ''.join(t.text or '' for run in para.findall(f'.//{W}r') for t in run.findall(f'{W}t'))

def get_para_type(text, idx):
    t = text.strip()
    if not t: return 'empty'
    if re.match(r'^\s*(目\s*录|Contents)', t): return 'toc'
    if re.search(r'参考文献', t): return 'reference'
    if re.match(r'^\s*\[?\d+[\]\.．]', t) and len(t) < 200: return 'reference'
    if (len(t) < 60 and not t.endswith('。') and not t.endswith('，') and
        (re.match(r'^[\d一二三四五六七八九十]+[\.、]', t) or
         re.match(r'^\s*(第[一二三四五六七八九十]+章|第[一二三四五六七八九十]+节)', t.replace(' ','')) or
         re.match(r'^\s*[\u4e00-\u9fa5]{2,15}$', t))):
        return 'heading'
    if re.search(r'图\s*\d', t) or re.search(r'表\s*\d', t): return 'figure_table'
    if re.search(r'^\s*\( ?[0-9一二三四五六七八九十]+ ?\)', t) and len(t) < 100: return 'equation_number'
    if re.match(r'^\s*\d+\s*$', t) and len(t) < 5: return 'page_number'
    if re.search(r'摘\s*要|ABSTRACT', t): return 'abstract'
    if re.search(r'致\s*谢|ACKNOWLEDGEMENT', t): return 'thanks'
    if re.search(r'图表目录|图目录|表目录|插图目录', t): return 'toc_figure'
    return 'body'

# Step 1: Find the exact file in Downloads
downloads_path = r'c:\Users\胡宠博\Downloads'
files = os.listdir(downloads_path)
target_files = [f for f in files if '免费' in f and '查重报告' in f and 'transformer' in f and f.endswith('.docx')]
print(f"Found files: {target_files}")

if not target_files:
    print("No matching files found!")
    exit(1)

docx_path = os.path.join(downloads_path, target_files[0])
print(f"Using: {docx_path}")

# Step 2: Open docx and read document.xml
with zipfile.ZipFile(docx_path, 'r') as z:
    xml_content = z.read('word/document.xml')

# Step 3: Parse XML
tree = etree.fromstring(xml_content)

# Step 4: Extract all paragraphs
all_paras = tree.findall(f'.//{W}p')

non_black_paragraphs = []

for idx, para in enumerate(all_paras):
    runs = para.findall(f'.//{W}r')
    colors = set()
    has_non_black = False
    
    for run in runs:
        color = get_run_color(run)
        if color and not is_black_color(color):
            has_non_black = True
            colors.add(color)
    
    if has_non_black:
        text = get_para_text(para)
        para_type = get_para_type(text, idx)
        non_black_paragraphs.append({
            'index': idx,
            'text': text,
            'colors': colors,
            'type': para_type
        })

# Step 5: Generate report
report_lines = []
report_lines.append("=" * 80)
report_lines.append("NON-BLACK COLOR PARAGRAPH SCAN REPORT")
report_lines.append("=" * 80)
report_lines.append(f"Source: {docx_path}")
report_lines.append(f"Total paragraphs in document: {len(all_paras)}")
report_lines.append(f"Total non-black paragraphs: {len(non_black_paragraphs)}")
report_lines.append("")

# Summary by type
type_counts = {}
for p in non_black_paragraphs:
    t = p['type']
    type_counts[t] = type_counts.get(t, 0) + 1

report_lines.append("-" * 80)
report_lines.append("SUMMARY BY TYPE:")
report_lines.append("-" * 80)
for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    report_lines.append(f"  {t}: {count}")
report_lines.append("")

# Full listing
report_lines.append("-" * 80)
report_lines.append("FULL LISTING OF NON-BLACK PARAGRAPHS:")
report_lines.append("-" * 80)

for p in non_black_paragraphs:
    report_lines.append("")
    report_lines.append(f"[Paragraph #{p['index']}]")
    report_lines.append(f"  Type: {p['type']}")
    report_lines.append(f"  Colors: {', '.join(sorted(p['colors']))}")
    report_lines.append(f"  Text ({len(p['text'])} chars):")
    # Word wrap at 76 chars
    text = p['text']
    for i in range(0, len(text), 76):
        report_lines.append(f"    {text[i:i+76]}")
    report_lines.append("")

# Print to console
print("\n".join(report_lines))

# Save to file
output_path = r'd:\transformer\thesis\color_scan_report.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(report_lines))

print(f"\nReport saved to: {output_path}")
