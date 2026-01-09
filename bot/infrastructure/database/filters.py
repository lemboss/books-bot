OPERATORS = {
    "eq": lambda col, val: col == val,
    "ne": lambda col, val: col != val,
    "gt": lambda col, val: col > val,
    "lt": lambda col, val: col < val,
    "gte": lambda col, val: col >= val,
    "lte": lambda col, val: col <= val,
    "like": lambda col, val: col.like(val),
    "ilike": lambda col, val: col.ilike(val),
    "in": lambda col, val: col.in_(val),
    "not_in": lambda col, val: ~col.in_(val),
    "between": lambda col, val: col.between(val[0], val[1]),
    "isnull": lambda col, val: col.is_(None) if val else col.is_not(None),
}