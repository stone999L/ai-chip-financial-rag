# 国产算力与智能芯片上市公司财报问答知识库

课程作业项目：基于上市公司 2026 年半年度报告，构建面向国产算力与智能芯片公司的财报问答知识库。

## 课程作业目标

- 覆盖至少 10 家上市公司
- 提取半年报正文与表格
- 每个文本块保留公司、证券代码、报告期、章节、页码等元数据
- 同时建立 BM25 与向量检索
- 通过混合检索为大模型提供可追溯证据
- 设计 10 道测试题，其中至少 2 道为跨公司全景题
- 记录召回结果、回答正确性与错误原因
- 最终交付 GitHub 代码仓库、系统页面截图与一页实验结论

## 样本公司

1. 寒武纪（688256）
2. 海光信息（688041）
3. 龙芯中科（688047）
4. 景嘉微（300474）
5. 芯原股份（688521）
6. 瑞芯微（603893）
7. 全志科技（300458）
8. 北京君正（300223）
9. 国科微（300672）
10. 复旦微电（688385）

统一报告期：2026 年半年度报告。

## 系统流程

```text
PDF 半年报
  ↓
文字 / 表格解析
  ↓
章节与页码识别
  ↓
切块 + 元数据
  ↓
BM25 索引 + 向量索引
  ↓
混合召回 / 去重
  ↓
大模型基于证据回答
  ↓
公司 + 报告期 + 页码 + 原文出处
```

## 目录

```text
ai-chip-financial-rag/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── reports_manifest.csv
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── download_reports.py
│   ├── parse_reports.py
│   ├── chunk_documents.py
│   └── build_index.py
├── src/
│   ├── config.py
│   ├── bm25_retriever.py
│   ├── vector_retriever.py
│   ├── hybrid_retriever.py
│   └── qa.py
├── app/
│   └── app.py
├── evaluation/
│   ├── questions.json
│   ├── evaluate.py
│   └── results.csv
├── screenshots/
└── conclusion/
    └── one_page_summary.md
```

## 实验原则

实验结果必须来自真实运行。仓库不会预先虚构准确率、召回率或正确率。跨公司全景题重点观察普通 top-k 检索是否遗漏部分公司，以及表格切块后是否出现报告期、公司或口径丢失。

## 当前进度

- [x] 建立项目仓库
- [x] 确定 10 家样本公司
- [x] 确定 10 道测试题框架
- [x] 核验并登记 10 份 2026 年半年度报告全文来源（source-check：10/10 下载及身份校验通过）
- [x] 下载与解析全部 PDF（10 份共 1,730 页；生成 5,073 个知识块，其中正文 2,367、表格 2,706）
- [x] 建立 BM25 与向量索引（正式实验：BAAI/bge-small-zh-v1.5 + BM25 + RRF）
- [x] 完成问答页面（Streamlit，可展示公司、章节、页码与原始 PDF 链接）
- [x] 跑完 10 道真实测试题并保存召回结果
- [x] 完成人工复核、错误分析、页面截图与一页结论


## 本地运行

建议 Python 3.11。

```bash
git clone https://github.com/stone999L/ai-chip-financial-rag.git
cd ai-chip-financial-rag

python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
copy .env.example .env
```

先检查样本清单：

```bash
python scripts/validate_manifest.py
```

完整流水线：

```bash
python scripts/run_pipeline.py
```

也可以分步运行：

```bash
python scripts/download_reports.py
python scripts/parse_reports.py
python scripts/chunk_documents.py
python scripts/build_index.py
```

建立索引后启动页面：

```bash
streamlit run app/app.py
```

运行 10 道题的检索记录：

```bash
python evaluation/evaluate.py
```

> 未配置 LLM API 时，页面仍可运行“证据检索模式”，直接展示 BM25 + 向量混合召回结果；这样可以先完成课程要求中的召回分析，再决定是否接入回答模型。


## 已验证的数据规模

GitHub Actions 的全量 `corpus-build` 已真实跑通：

- 10 份 2026 年半年度报告
- 共 1,730 页
- 5,073 个知识块
- 其中正文块 2,367 个
- 表格块 2,706 个
- 所有 10 家公司均被成功解析
- 原始 PDF 不提交到仓库，由 manifest 自动下载；处理结果作为 CI artifact 留存



## Embedding 模型选择说明

GitHub Actions 的普通 CPU runner 实测运行 Qwen3-Embedding-0.6B 时，batch_size=4 的前 7 个 batch 平均约 254 秒/批，1,269 批按线性估算约需 89.7 小时，不适合作为课程作业的可复现实验环境。因此 GitHub 云端正式实验改用 `BAAI/bge-small-zh-v1.5`，并把 batch_size 提高到 32。

`Qwen/Qwen3-Embedding-0.6B` 仍保留为 GPU 机器上的可选增强模型。检索框架、BM25、RRF 混合召回和评价题目均保持不变。


## 最终实验结果

正式 `retrieval-build` 已于 2026-09-29 在 GitHub Actions CPU runner 上成功完成：

- 5,073 个知识块全部建立 512 维向量；
- BM25 与 BGE-small 索引构建约 5 分 52 秒；
- 10 道检索题约 10 秒；
- 整个 retrieval workflow 约 7 分 11 秒；
- 10 题平均公司覆盖率：BM25 72%、向量检索 86%、RRF 混合检索 81%。

人工复核显示：Q2-Q6 的单公司问题证据充分；Q1 存在合并报表/母公司报表口径风险；Q7-Q10 暴露固定 Top-K 在多公司和全景问题上的覆盖不足。这里的 `answer_correct` 是基于人工参考答案和召回证据进行的“可回答性/证据充分性”复核，CI 未配置生成模型 API，因此不把它表述为自动 LLM 打分。

最终交付文件：

- `evaluation/retrieval_runs.csv`：10 道题的 BM25 / 向量 / 混合真实召回记录；
- `evaluation/results.csv`：人工复核后的正确性、证据充分性和错误类型；
- `evaluation/reference_answers.md`：人工参考答案与证据要求；
- `docs/experiment_results.md`：完整实验结果与错误分析；
- `conclusion/one_page_summary.md`：一页实验结论；
- `screenshots/query_demo_q3.svg`：典型成功案例静态结果页；
- `screenshots/query_demo_q9.svg`：跨公司全景题失败案例静态结果页。
