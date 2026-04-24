# AlphaTransformer 项目上下文

## 项目简介

AlphaTransformer 是一个「股票量化预测 + 前端可视化 + 代码知识图谱」三位一体的系统。

## 知识图谱

`graphify-out/graph.json`（3.5MB）是代码知识图谱，包含：

- **节点**：函数、文件、概念节点、理由链节点（`rationale_*`）
- **边类型**：`calls`、`imports_from`、`contains`、`provides`、`related_to`、`infers`、`derives`、`reasoned_by` 等
- **社区**：Louvain 算法划分的 112 个社区，每个社区有聚合主题名

### 读图流程

1. `grep` 找到目标模块/函数在 `graphify-out/graph.json` 中的节点 ID
2. 用 `jq` 查该节点的邻居和边类型
3. 用 `grep` 查同一社区内的高度数节点（god nodes）
4. 用 `grep` 查跨社区边（`reasoned_by`/`derives`/`infers`），理解模块间的推理关系

### 边类型说明

| 边类型 | 含义 |
|---|---|
| `calls` / `imports_from` / `contains` | 显式代码关系，直接可验证 |
| `infers` | 模型推断关系，需结合代码上下文判断 |
| `derives` | 数据推导关系，A 的输出是 B 的输入 |
| `reasoned_by` | 理由链，知识推理路径 |
| `AMBIGUOUS` | 置信度低，关系待确认 |

### 社区速查

| 模块 | 关键词 / 路径 | 社区 |
|---|---|---|
| 前端 (Vue 3 + Vite + Pinia + Element Plus) | `frontend/src/` | 社区 59–81 |
| 前端 API 层 | `frontend/src/api/index.ts` | 社区 9 |
| 技术指标 (SMA/EMA/RSI) | `technicals.ts` | 社区 49 |
| 图表配置 (ECharts) | `dashboard.ts`, `trade.ts`, `analysis.ts` | 社区 72–74 |
| AlphaTransformer 核心模型 | `alpha_transformer/` | 社区 2, 13, 19, 20 |
| Graphify 代码分析 | `graphify/graphify/` | 社区 0, 1, 4, 26 |
| Wiki 生成器 | `graphify/graphify/wiki.py` | 社区 22 |

## 前端结构

- `frontend/src/main.ts` → 加载 Vue + Pinia + Element Plus
- `frontend/src/App.vue` → 根组件
- `frontend/src/router/index.ts` → 路由（Dashboard / Analysis / Trade）
- `frontend/src/stores/` → Pinia stores：account、dashboard、ticker
- `frontend/src/api/index.ts` → HTTP 客户端；`cancelRequest()` / `getCancelToken()` 被广泛调用（度数 4）

## 操作规范

修改任何模块之前：

1. 读 `graphify-out/GRAPH_REPORT.md` 了解全局结构
2. 找到目标模块的节点 ID，查它的所有边
3. 确认函数/变量的度数（degree）和邻居类型
4. 如果涉及 `infers` 边，写代码时加上原理解释（rationale）

## 注意

- `rationale_*` 节点是 LLM 生成的推理记录，**不是代码**，不要修改
- 很多社区无主题名（只显示 "Community XX"），是低密度子图，不必关注
- 图生成命令：`python -m graphify graphify/ frontend/`
