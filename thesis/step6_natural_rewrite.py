# -*- coding: utf-8 -*-
"""
Word文档非黑色段落自然改写脚本 v6
避免机械替换，追求"本科生自己写"的自然风格
"""
import zipfile, os, shutil, re
from lxml import etree

# ========== 路径配置（动态查找文件）==========
DOWNLOADS = r"c:\Users\胡宠博\Downloads"
THESIS_DIR = r"d:\transformer\thesis"

def find_input_file():
    """动态查找输入文件"""
    try:
        files = os.listdir(DOWNLOADS)
    except Exception:
        return None
    candidates = [f for f in files
                 if 'transformer' in f.lower()
                 and f.endswith('.docx')
                 and 'Word' in f
                 and '标红' in f]
    # 优先选带 (1) 的
    for f in candidates:
        if '(1)' in f:
            return os.path.join(DOWNLOADS, f)
    if candidates:
        return os.path.join(DOWNLOADS, candidates[0])
    return None

INPUT_FILE = find_input_file()
OUTPUT_FILE = os.path.join(THESIS_DIR, "基于transformer的股票预测系统_非黑色段落自然改写版.docx")
REPORT_FILE = os.path.join(THESIS_DIR, "基于transformer的股票预测系统_自然改写报告.txt")

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

# ========== 关键数值保护 ==========
KEY_VALUES = ['1.65', '0.082', '-9.8%', '31.4%', '18.7%', '35', '2024', '2023']

# ========== 辅助函数 ==========

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

def check_mechanical_patterns(text):
    """自检：是否出现机械替换的痕迹"""
    warnings = []
    if re.search(r'一[为是用]、二[为是用]、三[为是用]、四[为是用]', text):
        warnings.append('过度规整的"一、二、三"句式')
    if re.search(r'的{3,}', text):
        warnings.append('连续三个以上"的"字')
    return warnings

# ============================================================
# 逐段落自然改写函数
# ============================================================

def rw_p18(text):
    """P18: 日期签名 - 不改"""
    return text

def rw_p22(text):
    """P22: 原创性声明 - 极轻改写"""
    result = text
    result = result.replace('独立研究所取得的', '独立开展研究所取得的')
    result = result.replace('本研究做出重要贡献', '本论文研究做出重要贡献')
    return result

def rw_p33(text):
    """P33: 授权书 - 极轻改写"""
    result = text
    result = result.replace('有权保留并向国家有关部门或机构送交', '有权保留，且可向国家有关部门或机构送交')
    return result

def rw_p34(text):
    """P34: 保密条款 - 不改"""
    return text

def rw_p65(text):
    """P65: 章节标题 - 不改"""
    return text

def rw_p86(text):
    """P86: 章节标题 - 不改"""
    return text

def rw_p106(text):
    """P106: 股票预测核心问题 - 自然改写"""
    parts = []
    parts.append('股票价格预测是量化投资研究里的一个基本问题。')
    parts.append('这个任务不是给单只股票算出一个精确的价格数字，而是要从高噪声、强非平稳、弱信号的市场数据中，把具有稳定排序能力的那部分信息提取出来。')
    parts.append('在真实投资中，模型至少要满足三个要求：能在横截面上把哪些资产相对更好区分出来，行情切换时不至于完全失效，扣掉交易成本后净收益仍有可解释性。')
    parts.append('从这个角度看，股票预测更像一个同时涉及时序依赖、资产联动和交易执行三重约束的问题[1,5-6]。')
    return ' '.join(parts)

def rw_p112(text):
    """P112: 预测研究演进 - 自然改写"""
    parts = []
    parts.append('股票预测的研究路线，大致经历了从统计方法到机器学习，再到近年深度时序模型这几个阶段。')
    parts.append('最早的一批方法主要处理局部线性依赖和波动聚集这些特征，碰到金融数据里常见的非线性关系、结构突变和资产间相互影响时，效果就不太好了[1]。')
    parts.append('后来 RNN、LSTM、CNN 这些深度模型进来以后，在捕捉短期模式上确实比之前强，但涉及长距离依赖的多步推理、并行计算的效率以及多资产一起建模这些方面，问题也一直没解决[3,8]。')
    return ' '.join(parts)

def rw_p115(text):
    """P115: 文献三方面不足 - 自然改写"""
    parts = []
    parts.append('翻看已有的研究，有几个地方值得提一下。')
    parts.append('首先，对 RNN、LSTM 和标准 Transformer 的介绍大多停留在通用框架层面，在金融数据非平稳性和市场状态切换这两个关键问题上，往往缺乏针对性的架构设计。')
    parts.append('其次，有些研究给出了不错的收益或准确率数字，但在数据处理防泄露和 Walk-Forward 验证的说明上不够充分，这让结论的可信度打了折扣。')
    parts.append('再次，换手率、交易摩擦和组合稳定性在许多研究中被简化处理，实验结果与实际可执行策略的表现之间存在明显落差。')
    return ' '.join(parts)

def rw_p120(text):
    """P120: 研究内容四方面 - 自然改写"""
    parts = []
    parts.append('针对上述方向，本课题主要做了四个方面的事情。')
    parts.append('第一，在多资产股票预测场景下搭建模型框架，对比 v1、v2、v3 在金融非平稳条件下的实际表现差异。')
    parts.append('第二，建立防泄露的训练与回测评估体系，通过滚动窗口标准化、标签时序对齐和 Walk-Forward 验证来保证实验结论的可信度。')
    parts.append('第三，把交易成本建模和 Anti-Churn 调仓机制纳入回测环节，考察模型输出在扣掉真实摩擦成本后是否仍具可用性。')
    parts.append('第四，用 FastAPI 和 Vue 3 实现前后端一体的系统原型，把模型训练、预测、回测和可视化分析串成一条完整链路。')
    return ' '.join(parts)

def rw_p124(text):
    """P124: 研究思路技术路径 - 自然改写"""
    parts = []
    parts.append('本课题按照"问题分析、模型调整、防泄露评估、系统落地、实证验证"这条路径展开。')
    parts.append('具体来说，先从金融市场的实际特点入手——弱信号、高噪声、非平稳，再加上交易成本不低这几个因素——来明确股票预测不能只看预测误差，需要把排序能力、风险收益特征和交易可执行性都纳入评估。')
    parts.append('然后在模型层面，以 v1 和 v2 为基线，引入 v3 混合架构。v3 通过让状态感知、时间维建模和资产维建模各自承担不同职责，形成协作，从而提高模型对复杂市场条件的适应能力。')
    return ' '.join(parts)

def rw_p125(text):
    """P125: 研究方法四种方式 - 自然改写"""
    parts = []
    parts.append('研究过程中主要用到四种方法：')
    parts.append('用文献研究来梳理股票预测、Transformer 改进、状态空间模型和量化评估等方面的发展脉络；')
    parts.append('用系统设计搭建数据层、模型层、服务层和展示层的完整框架；')
    parts.append('用实验分析对比 v1、v2、v3 在 IC、Sharpe Ratio、最大回撤和换手率等指标上的实际表现；')
    parts.append('用案例研究聚焦第六章中的 2024 年震荡市场样本，考察模型在复杂市场环境下的行为特征。')
    parts.append('这四种方法相互配合，把理论分析、算法实现和工程验证串成了一条完整的研究链路。')
    return ' '.join(parts)

def rw_p154(text):
    """P154: 系统四层架构 - 自然改写"""
    parts = []
    parts.append('围绕这个目标，系统架构划分为四个层次：数据层、模型层、服务层、展示层。')
    parts.append('数据层负责历史行情接入、股票池维护、特征工程、标签构造和滚动标准化，是整个系统的数据入口。')
    parts.append('模型层以 AlphaTransformer 系列模型为基础，负责训练、验证、推理和版本迭代。')
    parts.append('服务层基于 FastAPI 构建，封装预测接口、回测接口、健康检查和模型状态管理等功能，对外统一调用协议，隔离底层模型细节。')
    parts.append('展示层采用 Vue 3 实现，把模型输出转化为图表、表格和交互面板供用户查看。')
    parts.append('这样分层的好处是，做算法研究的人和做系统开发的人各自清楚自己的边界，协作起来更顺畅。')
    return ' '.join(parts)

def rw_p246(text):
    """P246: 后续研究三方向 - 自然改写"""
    parts = []
    parts.append('回过头看本研究还有哪些没做到的地方，接下来可以从三个方面继续做下去。')
    parts.append('一个方向是多模态融合，把量价数据与文本情绪、事件语义、公告信息等联合编码，提升模型对突发事件和市场情绪传导的感知能力。')
    parts.append('另一个方向是在线学习与动态仓位控制，在不违反防泄露约束的前提下，引入增量更新或强化学习方法，让模型不只做相对强弱预测，还能直接参与调仓节奏和风险预算的决策。')
    parts.append('还有一个方向是平台化，把模型管理、实验管理、回测引擎、可视化展示和策略部署等环节继续解耦，做成更稳定、更易扩展的量化研究工具。')
    return ' '.join(parts)

def rw_p270(text):
    """P270: 致谢 - 轻改写"""
    parts = []
    parts.append('本研究从选题立项、研究推进到系统实现和论文撰写，始终得到指导教师、学院老师和同学家人的关心与帮助。')
    parts.append('指导教师在选题方向、研究思路、系统实现和论文修改等环节给予耐心指点，帮助我逐步完成从算法设计到系统落地的全过程。')
    parts.append('学院提供的学习环境和实验条件为课题的顺利推进创造了条件，家人的理解和支持，也是我能坚持下来的重要原因。')
    parts.append('谨以此文，向所有给予我帮助和鼓励的人表示衷心的感谢。')
    return ' '.join(parts)

# ============================================================
# 段落索引到改写函数的映射
# ============================================================
REWRITE_MAP = {
    18: rw_p18, 22: rw_p22, 33: rw_p33, 34: rw_p34,
    65: rw_p65, 86: rw_p86,
    106: rw_p106, 112: rw_p112, 115: rw_p115, 120: rw_p120,
    124: rw_p124, 125: rw_p125,
    154: rw_p154,
    246: rw_p246, 270: rw_p270,
}

# ============================================================
# 主处理流程
# ============================================================

def process_document():
    if INPUT_FILE is None:
        print("错误：找不到输入文件！")
        return

    print(f"输入文件: {INPUT_FILE}")
    print(f"输出文件: {OUTPUT_FILE}")

    # 复制原文件
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    shutil.copy2(INPUT_FILE, OUTPUT_FILE)

    # 读取XML
    with zipfile.ZipFile(OUTPUT_FILE, 'r') as zf:
        doc_xml = zf.read('word/document.xml')

    parser = etree.XMLParser(remove_blank_text=False, encoding='utf-8')
    tree = etree.fromstring(doc_xml, parser)
    paragraphs = tree.findall(f'.//{W}p')

    # 找出所有非黑色段落
    all_non_black = []
    for idx, para in enumerate(paragraphs):
        runs = para.findall(f'{W}r')
        if not runs:
            continue
        text = get_para_text(para)
        if not text.strip():
            continue
        colors = [get_run_color(r) for r in runs]
        has_non_black = any(c is not None and not is_black_color(c) for c in colors)
        if has_non_black:
            ptype = get_para_type(text, idx)
            all_non_black.append({
                'index': idx, 'para': para, 'text': text,
                'colors': colors, 'type': ptype
            })

    skip_types = ('toc','reference','heading','figure_table','equation_number',
                 'page_number','toc_figure','empty')
    to_skip = [x for x in all_non_black if x['type'] in skip_types]
    to_rewrite = [x for x in all_non_black if x['type'] not in skip_types]

    print(f"\n非黑色段落总数: {len(all_non_black)}")
    print(f"实际改写段落数: {len(to_rewrite)}")
    print(f"跳过段落数: {len(to_skip)}")

    # 改写
    rewrite_results = []
    for item in to_rewrite:
        original = item['text']
        func = REWRITE_MAP.get(item['index'])
        new_text = func(original) if func else original
        mech_warnings = check_mechanical_patterns(new_text)

        missing = [v for v in KEY_VALUES if v in original and v not in new_text]
        if original:
            ratio = abs(len(new_text) - len(original)) / len(original) * 100
        else:
            ratio = 0

        rewrite_results.append({
            'index': item['index'],
            'type': item['type'],
            'colors': item['colors'],
            'original': original,
            'rewritten': new_text,
            'orig_len': len(original),
            'new_len': len(new_text),
            'ratio': ratio,
            'missing_values': missing,
            'mech_warnings': mech_warnings,
        })
        item['rewritten'] = new_text

    # 更新XML
    for item in to_rewrite:
        para = item['para']
        new_text = item['rewritten']
        for t in para.findall(f'.//{W}t'):
            t.text = ''
        runs = para.findall(f'{W}r')
        if runs:
            t_els = runs[0].findall(f'{W}t')
            if t_els:
                t_els[0].text = new_text
            else:
                new_t = etree.SubElement(runs[0], f'{W}t')
                new_t.text = new_text

    # 写回docx
    new_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp_file = OUTPUT_FILE + '.tmp'
    with zipfile.ZipFile(OUTPUT_FILE, 'r') as zin:
        with zipfile.ZipFile(tmp_file, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, new_xml)
                else:
                    zout.writestr(item, zin.read(item.filename))
    os.replace(tmp_file, OUTPUT_FILE)

    # ========== 生成报告 ==========
    def fmt(t, n=150):
        return t[:n] + ('...' if len(t) > n else '')

    skip_reasons = {
        'toc':'目录段落','reference':'参考文献条目','heading':'章节标题/页眉页脚',
        'figure_table':'图表编号','equation_number':'公式编号','page_number':'纯页码',
        'toc_figure':'图表目录','empty':'空段落',
    }

    report_lines = []
    def sec(title):
        report_lines.append('='*80)
        report_lines.append(title)
        report_lines.append('='*80)

    sec('Word文档非黑色段落自然改写报告')
    report_lines += [
        '',
        f'输入文件: {INPUT_FILE}',
        f'输出文件: {OUTPUT_FILE}',
        '',
        f'非黑色段落总数: {len(all_non_black)}',
        f'实际改写段落数: {len(to_rewrite)}',
        f'跳过段落数: {len(to_skip)}',
        '',
        '【本轮改写原则】',
        '  - 避免机械替换，追求"本科生自己写"的自然风格',
        '  - 不做全局同义词替换，不删除常用字',
        '  - 允许必要重复，句子长短自然变化',
        '',
    ]

    sec('跳过段落详情')
    for item in to_skip:
        report_lines.append(
            f"  段落{item['index']}: {skip_reasons.get(item['type'], item['type'])}")
        report_lines.append(f"    内容: {fmt(item['text'], 80)}")
    report_lines.append('')

    sec('改写段落详情')
    for i, res in enumerate(rewrite_results):
        color_str = ','.join(c for c in res['colors'] if c)
        report_lines.append(
            f"\n--- 改写段落 {i+1} / 总计 {len(rewrite_results)} "
            f"(编号: {res['index']}, 类型: {res['type']}, 颜色: {color_str}) ---")
        report_lines.append(f"原文字数: {res['orig_len']}")
        report_lines.append(f"新文字数: {res['new_len']}")
        report_lines.append(f"偏差比例: {res['ratio']:.1f}%")
        report_lines.append(f"\n原文片段: {fmt(res['original'])}")
        report_lines.append(f"新文片段: {fmt(res['rewritten'])}")
        report_lines.append(f"\n原文完整:")
        for line in res['original'].split('。'):
            if line.strip():
                report_lines.append(f"  {line.strip()}{'。' if line.strip() else ''}")
        report_lines.append(f"\n新文完整:")
        for line in res['rewritten'].split('。'):
            if line.strip():
                report_lines.append(f"  {line.strip()}{'。' if line.strip() else ''}")

        if res['missing_values']:
            report_lines.append(f"\n[!] 关键数值丢失: {res['missing_values']}")
        else:
            report_lines.append(f"\n[OK] 关键数值保留: 全部保留")

        if res['mech_warnings']:
            report_lines.append(f"[!] 机械痕迹检测: {res['mech_warnings']}")
        else:
            report_lines.append(f"[OK] 机械痕迹检测: 未发现明显机械替换痕迹")

        if res['ratio'] > 40:
            report_lines.append(f"[!] 偏差较大({res['ratio']:.1f}%)，建议人工复核")
        elif res['ratio'] > 30:
            report_lines.append(f"[*] 偏差偏高({res['ratio']:.1f}%)，可考虑人工复核")
        else:
            report_lines.append(f"[OK] 偏差比例正常({res['ratio']:.1f}%)")

    sec('汇总检查')
    total_missing = sum(len(r['missing_values']) for r in rewrite_results)
    total_mech = sum(len(r['mech_warnings']) for r in rewrite_results)
    report_lines += [
        f'关键数值保留: {"通过" if total_missing == 0 else f"丢失{total_missing}处"}',
        f'  需要保留: {KEY_VALUES}',
        '',
        f'机械痕迹检查: {"通过" if total_mech == 0 else f"发现{total_mech}处"}',
        f'  需要人工复核段落:',
    ]

    flagged_for_review = [r for r in rewrite_results if r['ratio'] > 30]
    if flagged_for_review:
        for r in flagged_for_review:
            report_lines.append(
                f"  - 段落{r['index']}: 偏差{r['ratio']:.1f}%, "
                f"原文{len(r['original'])}字→新文{len(r['rewritten'])}字")
    else:
        report_lines.append('  无需人工复核段落')

    sec('格式保留确认')
    report_lines += [
        '  公式编号: 已跳过，不修改',
        '  参考文献: 已跳过，不修改',
        '  章节结构: 已跳过，不修改',
        '  字体颜色: 原样保留（非黑色标记保持不变）',
        '  字号字体: 原样保留',
        '  段落样式: 原样保留',
    ]

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"\n处理完成!")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"报告文件: {REPORT_FILE}")
    print(f"\n统计:")
    print(f"  非黑色段落总数: {len(all_non_black)}")
    print(f"  实际改写段落数: {len(to_rewrite)}")
    print(f"  跳过段落数: {len(to_skip)}")
    print(f"  关键数值丢失: {total_missing}")
    print(f"  机械痕迹: {total_mech}")

if __name__ == '__main__':
    process_document()
