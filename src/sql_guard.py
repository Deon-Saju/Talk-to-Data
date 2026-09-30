import sqlglot
from sqlglot import exp
from src.config import MAX_ROWS

def validate(sql: str) -> str:
    """Return a safe, row-limited query or raise ValueError."""
    sql = sql.strip().rstrip(";")
    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except sqlglot.errors.ParseError as e:
        raise ValueError(f"Could not parse SQL: {e}")
    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Exactly one statement is allowed.")
    stmt = statements[0]
    if not isinstance(stmt, (exp.Select, exp.Union)):
        raise ValueError("Only SELECT queries are allowed.")
    if stmt.find(exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create):
        raise ValueError("Data-changing statements are not allowed.")
    return f"SELECT * FROM ({sql}) LIMIT {MAX_ROWS}"