"""Optional explicit edit budgets, independent of natural-language briefs."""
import math


def validate_budget(budget):
    if budget is None:return
    if not isinstance(budget,dict):raise ValueError('Duration budget must contain min_seconds and max_seconds')
    low,high=budget.get('min_seconds'),budget.get('max_seconds')
    if not all(type(x) in (int,float) and math.isfinite(x) for x in (low,high)) or not 0<=low<high:
        raise ValueError('Duration budget requires finite 0 <= min_seconds < max_seconds')


def require_duration(seconds,budget,tolerance=0):
    validate_budget(budget)
    if budget is not None and not budget['min_seconds']-tolerance<=seconds<=budget['max_seconds']+tolerance:
        raise ValueError(f"Edit duration {seconds:.3f}s outside budget {budget['min_seconds']}–{budget['max_seconds']}s")
