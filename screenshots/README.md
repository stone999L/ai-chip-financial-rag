# 页面截图

本目录保存基于 2026-09-29 GitHub Actions **真实检索结果**制作的结果页，用于课程作业提交与结果复核。

- `query_demo_q3.png`：PNG 版典型成功案例。Q3“海光信息 CPU 与 DCU 应用场景”中，BM25、向量和混合检索的目标公司覆盖均为 100%，人工复核为“证据充分”。
- `query_demo_q9.png`：PNG 版典型失败案例。Q9“10 家公司主要技术路线”中，BM25 / 向量 / 混合公司覆盖分别为 40% / 70% / 60%，显示普通固定 Top-K 无法保证全景覆盖。
- `query_demo_q3.svg`、`query_demo_q9.svg`：同一结果的矢量版，便于在报告或 PPT 中放大查看。

截图中的覆盖率和召回结论来自 `evaluation/retrieval_runs.csv` 与 `evaluation/results.csv`，不是虚构的性能数据。

> 说明：这些 PNG 是由真实实验数据生成的静态结果页，用于作业“页面截图”交付；交互式查询页面代码位于 `app/app.py`。
