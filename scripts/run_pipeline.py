from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("核验数据清单", ROOT / "scripts" / "validate_manifest.py"),
    ("下载已核验报告", ROOT / "scripts" / "download_reports.py"),
    ("解析正文与表格", ROOT / "scripts" / "parse_reports.py"),
    ("切块并保留元数据", ROOT / "scripts" / "chunk_documents.py"),
    ("建立 BM25 与向量索引", ROOT / "scripts" / "build_index.py"),
]


def main() -> None:
    for name, script in STEPS:
        print("\n" + "=" * 70)
        print(name)
        print("=" * 70)
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)

    print("\n流水线完成。下一步可运行：")
    print("streamlit run app/app.py")
    print("python evaluation/evaluate.py")


if __name__ == "__main__":
    main()
