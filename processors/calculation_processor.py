import re
import operator

from core.period_utils import normalize, normalize_period
from core.excel_utils import get_headers, get_value, set_value
from copy import copy


# generic math helpers

OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def to_number(value, skipped=None, column_name=None):
    if value in ("", None):
        if skipped is not None and column_name:
            skipped.add(column_name)
        return 0

    try:
        return float(value)
    except (ValueError, TypeError):
        if skipped is not None and column_name:
            skipped.add(column_name)
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
    

def copy_cell_style(source_cell, target_cell):
    if source_cell.has_style:
        target_cell.font = copy(source_cell.font)
        target_cell.fill = copy(source_cell.fill)
        target_cell.border = copy(source_cell.border)
        target_cell.alignment = copy(source_cell.alignment)
        target_cell.number_format = source_cell.number_format
        target_cell.protection = copy(source_cell.protection)


def is_june(month):
    return normalize_period(month).startswith("jun-")


def should_skip_calculation(config, calculation, month):
    category = normalize(config.get("category", ""))
    output_column = normalize(calculation.get("output_column", ""))

    if (
        category == normalize("recyclable_wastes")
        and output_column == normalize("Yearly Total Waste Generated")
        and not is_june(month)
    ):
        return True

    return False
    

def data_processing(target_wb, config):

    def calculate_sum(values):
        return sum(to_number(value) for value in values)

    def calculate_average(values):
        values = [to_number(value) for value in values]
        if not values:
            return 0
        return sum(values) / len(values)

    def calculate_rolling_sum(values, window):
        return sum(to_number(value) for value in values[-window:])

    def calculate_rolling_average(values, window):
        values = values[-window:]
        if not values:
            return 0
        return calculate_average(values)

    def calculate_percentage(numerator, denominator):
        denominator = to_number(denominator)
        if denominator == 0:
            return 0
        return to_number(numerator) / denominator

    def find_calculation_period_row(ws, period):
        wanted = normalize_period(period)

        for row in range(2, ws.max_row + 1):
            value = ws.cell(row=row, column=1).value

            if normalize_period(value) == wanted:
                return row

        return ws.max_row + 1

    def get_selected_months(source_ws, source_headers):
        settings = config.get("calculation_months", {})
        mode = settings.get("mode", "selected")

        period_col = 1

        all_months = [
            source_ws.cell(row=row, column=period_col).value
            for row in range(2, source_ws.max_row + 1)
            if source_ws.cell(row=row, column=period_col).value not in ("", None)
        ]

        if mode == "selected":
            return settings.get("months", [])

        if mode == "all":
            return all_months

        if mode == "range":
            start = normalize_period(settings["start"])
            end = normalize_period(settings["end"])

            selected = []
            in_range = False

            for month in all_months:
                current = normalize_period(month)

                if current == start:
                    in_range = True

                if in_range:
                    selected.append(month)

                if current == end:
                    break

            return selected

        raise ValueError(f"Unsupported calculation_months mode: {mode}")

    def read_values(ws, headers, row, column_names, skipped_non_numeric):
        skipped_columns = set()
        values = []

        for column_name in column_names:
            raw_value = get_value(ws, row, headers, column_name, skipped_columns)
            values.append(to_number(raw_value, skipped_non_numeric, column_name))

        return values

    def read_rolling_values(ws, headers, current_row, column_name, lookback_months, skipped_non_numeric):
        skipped_columns = set()
        start_row = max(2, current_row - lookback_months + 1)
        values = []

        for row in range(start_row, current_row + 1):
            raw_value = get_value(ws, row, headers, column_name, skipped_columns)
            values.append(to_number(raw_value, skipped_non_numeric, column_name))

        return values

    source_ws = target_wb[config["calculation_source_sheet"]]
    target_ws = target_wb[config["calculation_target_sheet"]]

    source_headers = get_headers(source_ws, 1)
    target_headers = get_headers(target_ws, 1)

    months = get_selected_months(source_ws, source_headers)
    calculations = config.get("calculations", {})

    processed_updates_by_month = {}
    skipped_non_numeric_by_month = {}

    for month in months:
        source_row = find_calculation_period_row(source_ws, month)
        target_row = find_calculation_period_row(target_ws, month)

        target_ws.cell(row=target_row, column=1).value = month

        for calculation_name, calculation in calculations.items():
            skipped_non_numeric = set()

            calc_type = calculation["type"]
            output_column = calculation["output_column"]

            if should_skip_calculation(config, calculation, month):
                continue

            if "source_items" in calculation:
                values = read_values(
                    source_ws,
                    source_headers,
                    source_row,
                    calculation["source_items"],
                    skipped_non_numeric
                )

            elif "input_columns" in calculation:
                values = read_values(
                    target_ws,
                    target_headers,
                    target_row,
                    calculation["input_columns"],
                    skipped_non_numeric
                )

            elif "input_column" in calculation:
                values = read_rolling_values(
                    target_ws,
                    target_headers,
                    target_row,
                    calculation["input_column"],
                    calculation.get("lookback_months", 12),
                    skipped_non_numeric
                )

            else:
                print(f"Skipped calculation with no inputs: {calculation_name}")
                continue

            if calc_type == "sum":
                result = calculate_sum(values)

            elif calc_type == "average":
                result = calculate_average(values)

            elif calc_type == "rolling_sum":
                result = calculate_rolling_sum(
                    values,
                    calculation.get("lookback_months", 12)
                )

            elif calc_type == "rolling_average":
                result = calculate_rolling_average(
                    values,
                    calculation.get("lookback_months", 12)
                )

            elif calc_type == "percentage":
                result = calculate_percentage(
                    values[0] if len(values) > 0 else 0,
                    values[1] if len(values) > 1 else 0
                )

            else:
                raise ValueError(f"Unsupported calculation type: {calc_type}")

            output_col = target_headers.get(normalize(output_column))

            if not output_col:
                print(f"Skipped missing output column: {output_column}")
                continue

            cell = target_ws.cell(row=target_row, column=output_col)

            if target_row > 2:
                copy_cell_style(
                    target_ws.cell(row=target_row - 1, column=output_col),
                    cell
                )

            cell.value = result

            processed_updates_by_month.setdefault(
                normalize_period(month),
                []
            ).append(output_column)

            if skipped_non_numeric:
                skipped_non_numeric_by_month.setdefault(normalize_period(month), set()).update(
                    skipped_non_numeric
                )

            if calc_type == "percentage":
                cell.number_format = "0%"
            else:
                cell.number_format = "#,##0"
            
    print("\nProcessed data calculations:")

    if processed_updates_by_month:

        grouped = []

        for month, updated_columns in processed_updates_by_month.items():

            expected_outputs = [
                calculation["output_column"]
                for calculation in calculations.values()
                if not should_skip_calculation(config, calculation, month)
            ]

            updated_columns = sorted(set(updated_columns))

            if set(updated_columns) == set(expected_outputs):
                summary = "All"
            else:
                summary = ", ".join(updated_columns)

            if not grouped:
                grouped.append([month, month, summary])

            elif grouped[-1][2] == summary:
                grouped[-1][1] = month

            else:
                grouped.append([month, month, summary])

        for start, end, summary in grouped:
            if start == end:
                print(f"- {start} | {summary}")
            else:
                print(f"- {start} to {end} | {summary}")

    else:
        print("- none")

    
    print("\nBlank / non-numeric values not counted:")

    if skipped_non_numeric_by_month:
        for month, columns in skipped_non_numeric_by_month.items():
            print(f"- {month} | {', '.join(sorted(columns))}")
    else:
        print("- none")