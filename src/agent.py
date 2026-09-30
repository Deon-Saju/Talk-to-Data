from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from src.db import get_conn, get_schema as _schema
from src.sql_guard import validate
from src.llm import get_llm

_log = []  # queries run during the current question: {"sql", "columns", "rows"}

@tool
def get_schema() -> str:
    """Return all table names and their columns."""
    return _schema()

@tool
def run_sql(query: str) -> str:
    """Run one read-only SQLite SELECT query and return the rows."""
    try:
        safe = validate(query)
        conn = get_conn()
        cur = conn.execute(safe)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        conn.close()
        _log.append({"sql": query, "columns": cols, "rows": rows})
        return f"columns: {cols}\nrows: {rows}"
    except Exception as e:
        return f"ERROR: {e}"   # the model reads this and retries

TOOLS = {"get_schema": get_schema, "run_sql": run_sql}

SYSTEM = """You are a data analyst assistant for a Brazilian e-commerce database (SQLite, Olist).
Rules:
- Call get_schema first if you are unsure about tables or columns.
- Write SQLite SQL and run it with run_sql. If you get an ERROR, fix the query and retry.
- Revenue = SUM(order_items.price). Freight is order_items.freight_value.
- Product categories are in products.product_category_name (Portuguese); English names
  are in product_category_name_translation (product_category_name -> product_category_name_english).
- Dates are TEXT like '2017-10-02 10:56:33'; use strftime() for grouping by month or year.
- Only count orders with order_status = 'delivered' unless the question says otherwise.
- Answer in plain language for a non-technical reader and include the key numbers.
- Never invent numbers. If a query returns nothing, say so."""

llm = get_llm().bind_tools(list(TOOLS.values()))

def _text(content) -> str:
    if isinstance(content, list):
        return "".join(
            p.get("text", "") for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        )
    return content

def ask(question: str, max_steps: int = 6) -> dict:
    _log.clear()
    messages = [SystemMessage(SYSTEM), HumanMessage(question)]
    for _ in range(max_steps):
        ai = llm.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            return {
                "answer": _text(ai.content),
                "sql": [q["sql"] for q in _log],
                "data": _log[-1] if _log else None,
            }
        for call in ai.tool_calls:
            result = TOOLS[call["name"]].invoke(call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return {
        "answer": "Sorry, I couldn't finish that within the step limit.",
        "sql": [q["sql"] for q in _log],
        "data": None,
    }

if __name__ == "__main__":
    out = ask("Which 5 product categories have the highest total revenue?")
    print(out["answer"])
    print("\nSQL used:")
    for q in out["sql"]:
        print(q)