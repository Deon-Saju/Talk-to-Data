import json
import math
import os
import sys
import time
from pathlib import Path

from src.agent import ask
from src.db import get_conn

EVAL_FILE = Path("tests/eval_questions.json")


def same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-4, abs_tol=0.011)
    return a == b


def row_matches(gold_row, agent_row):
    """Every gold value must appear in the agent row (extra columns are allowed)."""
    pool = list(agent_row)
    for g in gold_row:
        for i, a in enumerate(pool):
            if same(g, a):
                pool.pop(i)
                break
        else:
            return False
    return True


def results_match(gold_rows, agent_rows):
    if len(gold_rows) != len(agent_rows):
        return False
    unused = list(agent_rows)
    for g in gold_rows:
        for i, a in enumerate(unused):
            if row_matches(g, a):
                unused.pop(i)
                break
        else:
            return False
    return True


def run_gold(sql):
    conn = get_conn()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def main():
    items = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(items)
    results, passed = [], 0

    for n, item in enumerate(items[:limit], start=1):
        q = item["question"]
        try:
            gold = run_gold(item["gold_sql"])
        except Exception as e:
            print(f"[{n}] GOLD SQL ERROR - fix the test: {q}\n     {e}")
            continue

        start = time.time()
        error, agent_sql, ok = None, [], False
        try:
            out = ask(q)
            agent_sql = out.get("sql", [])
            data = out.get("data")
            ok = bool(data) and results_match(gold, data["rows"])
        except Exception as e:
            error = str(e)[:200]
        elapsed = round(time.time() - start, 1)

        passed += ok
        print(f"[{n}] {'PASS' if ok else 'FAIL'} ({elapsed}s) {q}")
        if not ok:
            print(f"     gold rows : {gold[:3]}")
            print(f"     agent SQL : {agent_sql[-1] if agent_sql else error}")
        results.append({"question": q, "passed": ok, "seconds": elapsed,
                        "agent_sql": agent_sql, "error": error})
        time.sleep(2)  # be gentle with free-tier rate limits

    total = len(results)
    if total == 0:
        print("No questions were run.")
        return
    avg = round(sum(r["seconds"] for r in results) / total, 1)
    provider = os.getenv("LLM_PROVIDER", "groq")
    model = os.getenv("MODEL_NAME", "default")
    print(f"\nAccuracy: {passed}/{total} = {passed / total:.0%} | avg {avg}s | {provider}:{model}")

    name = f"tests/results_{provider}_{model}".replace("/", "_") + ".json"
    Path(name).write_text(json.dumps(
        {"provider": provider, "model": model, "accuracy": passed / total,
         "avg_seconds": avg, "results": results}, indent=2), encoding="utf-8")
    print(f"Saved details to {name}")


if __name__ == "__main__":
    main()