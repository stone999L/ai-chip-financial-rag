# 页面截图

本目录保存基于 2026-09-29 GitHub Actions 真实检索结果制作的静态结果页，用于课程作业提交与结果复核。

- `query_demo_q3.svg`：典型成功案例。Q3“海光信息 CPU 与 DCU 应用场景”中，BM25、向量和混合检索的目标公司覆盖均为 100%，人工复核为“证据充分”。
- `query_demo_q9.svg`：典型失败案例。Q9“10 家公司主要技术路线”中，BM25 / 向量 / 混合公司覆盖分别为 40% / 70% / 60%，显示普通固定 Top-K 无法保证全景覆盖。

页面中的覆盖率和召回结论来自 `evaluation/retrieval_runs.csv` 与 `evaluation/results.csv`，不是手工虚构的性能数据。
