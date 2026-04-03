"""
分析参考论文的格式规范
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def analyze_paragraph_format(para):
    """分析段落格式"""
    info = {
        'text': para.text[:80] + '...' if len(para.text) > 80 else para.text,
        'alignment': str(para.alignment) if para.alignment else 'None',
        'style_name': para.style.name if para.style else 'None',
        'runs': []
    }
    
    for run in para.runs:
        run_info = {
            'text': run.text[:50] + '...' if len(run.text) > 50 else run.text,
            'font_name': run.font.name,
            'font_size': run.font.size,
            'bold': run.font.bold,
            'italic': run.font.italic,
            'underline': run.underline,
            'color': str(run.font.color.rgb) if run.font.color and run.font.color.rgb else 'None'
        }
        info['runs'].append(run_info)
    
    return info

def analyze_document(doc_path):
    """分析文档结构"""
    doc = Document(doc_path)
    
    print("=" * 80)
    print("文档结构分析报告")
    print("=" * 80)
    
    # 1. 页面设置
    section = doc.sections[0]
    print(f"\n【页面设置】")
    print(f"  页面尺寸: {section.page_width.cm:.2f}cm x {section.page_height.cm:.2f}cm")
    print(f"  页边距: 上={section.top_margin.cm:.2f}cm, 下={section.bottom_margin.cm:.2f}cm, 左={section.left_margin.cm:.2f}cm, 右={section.right_margin.cm:.2f}cm")
    
    # 2. 样式列表
    print(f"\n【文档样式】")
    for style in doc.styles:
        if style.type.name == 'PARAGRAPH' and style.name.startswith(('Heading', 'Normal', 'Title')):
            try:
                print(f"  {style.name}")
            except:
                pass
    
    # 3. 分析前20个段落
    print(f"\n【段落格式分析（前30个段落）】")
    for i, para in enumerate(doc.paragraphs[:30]):
        if para.text.strip():
            info = analyze_paragraph_format(para)
            print(f"\n段落 {i+1}:")
            print(f"  样式: {info['style_name']}")
            print(f"  对齐: {info['alignment']}")
            if info['runs']:
                print(f"  首字符格式:")
                r = info['runs'][0]
                print(f"    字体: {r['font_name']}, 大小: {r['font_size']}, 粗体: {r['bold']}")
    
    # 4. 查找标题样式
    print(f"\n【标题层级分析】")
    headings = {'Heading 1': [], 'Heading 2': [], 'Heading 3': []}
    for i, para in enumerate(doc.paragraphs):
        if para.style and para.style.name in headings:
            headings[para.style.name].append((i+1, para.text[:50]))
    
    for style, items in headings.items():
        if items:
            print(f"\n{style}:")
            for num, text in items[:5]:
                print(f"  {num}. {text}")
    
    # 5. 字体统计
    print(f"\n【字体使用统计】")
    fonts = {}
    sizes = {}
    for para in doc.paragraphs:
        for run in para.runs:
            if run.font.name:
                fonts[run.font.name] = fonts.get(run.font.name, 0) + 1
            if run.font.size:
                sizes[str(run.font.size)] = sizes.get(str(run.font.size), 0) + 1
    
    print("常用字体:")
    for font, count in sorted(fonts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {font}: {count}处")
    
    print("常用字号:")
    for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {size}: {count}处")
    
    # 6. 表格分析
    print(f"\n【表格数量】: {len(doc.tables)}")
    
    # 7. 图片数量
    print(f"\n【图片/嵌入式对象数量】: {len(doc.inline_shapes)}")

if __name__ == "__main__":
    doc_path = r"c:\Users\胡宠博\Downloads\参考论文-基于自然语言处理的银行智能语音助手的设计与实现-智能系统类.docx"
    analyze_document(doc_path)
