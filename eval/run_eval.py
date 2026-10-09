import json
from pathlib import Path
import pandas as pd

from app.core.tools import TOOL_MAP

DATA = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"
CASES = Path(__file__).resolve().parent / "cases.json"

def main():
    df = pd.read_csv(DATA)
    cases = json.loads(CASES.read_text())
    print("Local tool evaluation")
    print("=" * 60)
    for case in cases:
        available = all(name in TOOL_MAP for name in case["expected_tools"])
        print(f"{case['name']}: {'PASS' if available else 'FAIL'}")
    print("Tool declarations available:", len(TOOL_MAP))

if __name__ == "__main__":
    main()
