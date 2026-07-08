import re
import operator

from core.period_utils import normalize


# system calculates excel formulas before comparing
OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def to_number(value):
    if value in ("", None):
        return 0

    try:
        return float(value)
    except (ValueError, TypeError):
        return 0
    

def round_to_reporting(value):
    value = to_number(value)
    return round(value, -1)


def convert_to_kg(category_name, value):

    if value in ("", None):
        return 0

    value = to_number(value)

    tonne_categories = {
        normalize("General Waste"),
        normalize("General Wastes"),
        normalize("Trash"),
        normalize("Yellow Skip"),
        normalize("Yellow skip"),
    }

    if normalize(category_name) in tonne_categories:
        return value * 1000
    
    if normalize(category_name) == normalize("Trash"):
        value = round(value, -1)

    return value


def resolve_cell_value(ws, value):
    if isinstance(value, str) and value.startswith("="):
        return calculate_simple_formula(ws, value)

    return value


def calculate_simple_formula(ws, formula):
    original_formula = formula

    formula = formula.strip().lstrip("=")

    # handles number related formulas in excel
    if re.fullmatch(r"\s*-?\d+(?:\.\d+)?(?:\s*[+\-*/]\s*-?\d+(?:\.\d+)?)+\s*", formula):
        try:
            return eval(formula, {"__builtins__": {}})
        except Exception:
            return original_formula

    # handles position related formulas in excel e.g. =Y146-Z146
    match = re.fullmatch(r"\s*([A-Z]+\d+)\s*([+\-*/])\s*([A-Z]+\d+)\s*", formula)
    if match:
        left_cell, op, right_cell = match.groups()

        left_value = resolve_cell_value(ws, ws[left_cell].value)
        right_value = resolve_cell_value(ws, ws[right_cell].value)

        try:
            left_value = float(left_value)
            right_value = float(right_value)

            if op == "+":
                return left_value + right_value
            if op == "-":
                return left_value - right_value
            if op == "*":
                return left_value * right_value
            if op == "/":
                return left_value / right_value
        except Exception:
            return original_formula

    return original_formula


# compare differences in value

def values_different(a, b):
    if a in ("", None) and b in ("", None):
        return False

    try:
        return abs(float(a) - float(b)) > 0.01
    except (ValueError, TypeError):
        return str(a).strip() != str(b).strip()
    

def numeric_difference(a, b):
    try:
        return abs(float(a) - float(b))
    except (ValueError, TypeError):
        return None