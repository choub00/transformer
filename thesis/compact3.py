import sys, re
sys.stdout.reconfigure(encoding='utf-8')
with open(r'd:/transformer/thesis/paper_final.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1.3 - use line-by-line replacement
lines = content.split('\n')
new_lines = []
skip_count = 0
for i, line in enumerate(lines):
    # Skip lines 36-46 (0-indexed: 35-45) which are the 5 bullet point headers
    # But we need to be more precise - skip the blank lines between and keep content
    pass

# Better approach: find and replace the whole block
start = None
end = None
for i, line in enumerate(lines):
    if '尽管深度学习在股票预测领域已取得诸多进展' in line:
        start = i
    if '许多预测模型"收益高而 Sharpe 低"，本质原因在于信号有效性不足以覆盖高频交易摩擦。' in line:
        end = i

if start is not None and end is not None:
    print(f"Found block at lines {start}-{end}")
    # Replace the whole block
    new_block = '尽管深度学习已取得诸多进展，但现有研究仍存在以下关键瓶颈：第一，传统模型对复杂非线性时序模式识别能力不足，金融市场中的价格演化是多主体博弈与流动性冲击共同作用的结果，传统统计模型难以表达突发跳变和多因子交互；第二，标准 Transformer 在长序列场景下面临 \(O(n^2)\) 复杂度瓶颈，分钟级行情数据的注意力矩阵带来显著显存占用与计算延迟；第三，极端市场状态下模型泛化能力不足，不同阶段在波动率和行业轮动速度方面差异显著，模型容易在平稳期表现良好而在极端行情中失效；第四，回测流程中数据泄露问题突出，使用全样本统计量或引用未来时点信息会使回测结果被系统性高估；第五，高换手率导致策略收益被交易摩擦显著侵蚀，"收益高而 Sharpe 低"的本质原因是信号有效性不足以覆盖高频交易摩擦。'
    lines = lines[:start] + [new_block] + lines[end+1:]
    content = '\n'.join(lines)
    print("1.3 replaced")
else:
    print("Block not found")

with open(r'd:/transformer/thesis/paper_final.md', 'w', encoding='utf-8') as f:
    f.write(content)

chinese = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
english_letters = len(re.findall(r'[a-zA-Z]', content))
total = chinese + english_letters
print(f"Total: {total}")
print(f"Target: 13000-18000")
print(f"OK: {13000 <= total <= 18000}")
