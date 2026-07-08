import openpyxl

from core.period_utils import (
    normalize,
    parse_period,
    normalize_period,
    first_day_of_month,
    subtract_months,
)

from core.excel_utils import (
    find_first_header_row,
    get_headers,
    get_value,
    set_value,
    find_period_row,
    flag_inconsistency,
    keep_only_relevant_sheets,
)

from processors.calculation_processor import (
    resolve_cell_value,
    values_different,
    numeric_difference,
)


# make sure new building is added after all previous buildings instead of end of sheet
def find_last_building_column(headers, config):
    last_col = 0

    for target_col in config["column_map"].keys():
        col = headers.get(normalize(target_col))
        if col and col > last_col:
            last_col = col

    return last_col


# new buildings may be added to Excel. automatically update new column to target
def add_new_source_columns_to_output(
    source_ws,
    target_ws,
    source_header_row,
    target_header_row,
    source_headers,
    target_headers,
    start_date,
    end_date,
    config
):
    new_columns = []

    mapped_source_columns = {normalize(source_col) for source_col in config["column_map"].values()}
    mapped_source_columns.add(normalize("Period"))

    for cell in source_ws[source_header_row]:
        if not cell.value:
            continue

        source_header_name = str(cell.value).strip()
        normalized_source_name = normalize(source_header_name)

        if normalized_source_name in mapped_source_columns:
            continue

        if normalized_source_name not in target_headers:
            new_col_num = find_last_building_column(target_headers, config) + 1

            target_ws.insert_cols(new_col_num)
            target_ws.cell(row=target_header_row, column=new_col_num).value = source_header_name

            target_headers.clear()
            target_headers.update(get_headers(target_ws, target_header_row))

            config["column_map"][source_header_name] = source_header_name
            new_columns.append(source_header_name)
        else:
            new_col_num = target_headers[normalized_source_name]
            config["column_map"][source_header_name] = source_header_name

        period_col = target_headers.get(normalize("Period"))

        if not period_col:
            raise ValueError("Could not find Period column after inserting new column")

        for row in range(target_header_row + 1, target_ws.max_row + 1):
            period_value = target_ws.cell(row=row, column=period_col).value
            period_date = parse_period(period_value)

            if period_date is None:
                continue

            period_month = first_day_of_month(period_date)

            if period_month <= end_date:
                if target_ws.cell(row=row, column=new_col_num).value in ("", None):
                    target_ws.cell(row=row, column=new_col_num).value = 0

    return new_columns


def process_electricity(config):
    skipped_columns = set()
    inconsistencies = []

    source_wb = openpyxl.load_workbook(config["source_file"], data_only=True)
    source_wb_highlight = openpyxl.load_workbook(config["source_file"], data_only=True)
    target_wb = openpyxl.load_workbook(config["target_file"])

    source_ws = source_wb[config["source_sheet"]]
    source_ws_highlight = source_wb_highlight[config["source_sheet"]]
    target_ws = target_wb[config["target_sheet"]]

    source_header_row = find_first_header_row(source_ws, "Period")
    target_header_row = find_first_header_row(target_ws, "Period")

    source_headers = get_headers(source_ws, source_header_row)
    target_headers = get_headers(target_ws, target_header_row)

    # end_date = last recorded month in source
    source_period_col = source_headers.get(normalize("Period"))

    if not source_period_col:
        raise ValueError("Could not find Period column in source file")

    source_months = []

    for source_row in range(source_header_row + 1, source_ws.max_row + 1):
        period_value = source_ws.cell(row=source_row, column=source_period_col).value
        period_date = parse_period(period_value)

        if period_date is not None:
            source_months.append(first_day_of_month(period_date))

    if not source_months:
        raise ValueError("No valid periods found in source file")

    end_date = max(source_months)
    start_date = subtract_months(end_date, config["lookback_months"])

    new_columns = add_new_source_columns_to_output(
        source_ws,
        target_ws,
        source_header_row,
        target_header_row,
        source_headers,
        target_headers,
        start_date,
        end_date,
        config
    )

    for source_row in range(source_header_row + 1, source_ws.max_row + 1):  # locate header row and read onwards
        period_value = source_ws.cell(row=source_row, column=source_period_col).value
        period_date = parse_period(period_value)

        if period_date is None:
            continue

        period_month = first_day_of_month(period_date)

        if not (start_date <= period_month <= end_date):
            continue

        target_row = find_period_row(target_ws, target_headers, period_value)

        set_value(
            target_ws,
            target_row,
            target_headers,
            "Period",
            period_value,
            skipped_columns
        )

        for target_col, source_col in config["column_map"].items():
            source_value = get_value(
                source_ws,
                source_row,
                source_headers,
                source_col,
                skipped_columns
            )

            target_col_num = target_headers.get(normalize(target_col))

            if not target_col_num:
                skipped_columns.add(target_col)
                continue

            existing_target_value = resolve_cell_value(
                target_ws,
                target_ws.cell(row=target_row, column=target_col_num).value
            )

            if (
                target_col not in new_columns
                and existing_target_value not in ("", None)
                and source_value not in ("", None)
                and values_different(existing_target_value, source_value)
            ):
                diff = numeric_difference(existing_target_value, source_value)

                # automatically update if the numeric difference is less than 1
                if diff is None or diff >= 1:
                    flag_inconsistency(
                    target_ws,
                    source_ws_highlight,
                    target_row,
                    target_col_num,
                    source_row,
                    source_headers.get(normalize(source_col)),
                    inconsistencies,
                    period_value,
                    target_col,
                    existing_target_value,
                    source_value
                )
                    continue
            
            # make sure it doesn't override existing 0 with blank if new building
            if source_value in ("", None):
                pass
            else:
                target_ws.cell(row=target_row, column=target_col_num).value = source_value

    keep_only_relevant_sheets(target_wb, config["target_sheet"])
    target_wb.save(config["target_output_file"])
    
    source_wb_highlight.save(config["source_output_file"])

    print(f"\nSuccess. Saved as {config['target_output_file']}")
    print(f"Highlighted source copy saved as {config['source_output_file']}")

    print(
        f"This application compared and transferred data only within the "
        f"last {config['lookback_months']} months "
        f"({start_date.strftime('%b %y')} to {end_date.strftime('%b %y')})."
    )

    if new_columns:
        print("\nNew source columns detected and added to output:")
        for col in new_columns:
            print(f"- {col}")
            print(
            "Previous months were filled with 0, and available source data "
            "has already been updated in the output Excel file."
            )

    if skipped_columns:
        print("\nMissing columns (possibly due to naming error):")
        for col in sorted(skipped_columns):
            print(f"- {col}")
    else:
        print("\nNo columns were skipped.")

    if inconsistencies:
        print("\n=============")
        print("\nNOTE:")
        print("Cells with inconsistencies were NOT overwritten.")
        print("The existing values in the target workbook were preserved.")

        print("\nInconsistencies found:")

        print("\nSUST office reference - output workbook cell numbers:")
        for item in inconsistencies:
            print(
                f"- {item['period']} | {item['column']} ({item['target_cell']}): "
                f"SUST had {item['existing_target_value']}, "
                f"source has {item['new_source_value']}"
            )

        print("\nOther department reference - source workbook cell numbers:")
        for item in inconsistencies:
            print(
                f"- {item['period']} | {item['column']} ({item['source_cell']}): "
                f"SUST had {item['existing_target_value']}, "
                f"source has {item['new_source_value']}"
            )

    else:
        print("\nNo inconsistencies found.")