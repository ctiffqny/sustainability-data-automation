from core.period_utils import normalize
from core.excel_format_utils import copy_column_format_from_source

def find_source_separator_after(source_ws, source_header_row, source_col):
    separator_col = source_col + 1

    if separator_col <= source_ws.max_column:
        if source_ws.cell(row=source_header_row, column=separator_col).value in ("", None):
            return separator_col

    return None

def find_previous_source_header_in_target(
    source_ws,
    source_header_row,
    source_col_num,
    target_headers,
):
    for col in range(source_col_num - 1, 0, -1):
        value = source_ws.cell(row=source_header_row, column=col).value

        if value in ("", None):
            continue

        if normalize(value) == normalize("Period"):
            continue

        target_col = target_headers.get(normalize(value))

        if target_col:
            return col, target_col

    return None, None


def ensure_source_separators_exist(
    source_ws,
    target_ws,
    source_header_row,
    target_header_row,
    previous_source_col,
    previous_target_col,
    current_source_col,
):
    target_insert_col = previous_target_col + 1

    for source_col in range(previous_source_col + 1, current_source_col):
        source_value = source_ws.cell(
            row=source_header_row,
            column=source_col,
        ).value

        if source_value not in ("", None):
            continue

        if target_ws.cell(
            row=target_header_row,
            column=target_insert_col,
        ).value not in ("", None):
            target_ws.insert_cols(target_insert_col)

        copy_column_format_from_source(
            source_ws,
            target_ws,
            source_col,
            target_insert_col,
            source_header_row,
            target_header_row,
        )

        target_insert_col += 1

    return target_insert_col


def copy_source_separator_after_if_exists(
    source_ws,
    target_ws,
    source_header_row,
    target_header_row,
    source_col_num,
    target_col_num,
):
    source_separator_col = source_col_num + 1

    if source_separator_col > source_ws.max_column:
        return

    if source_ws.cell(
        row=source_header_row,
        column=source_separator_col,
    ).value not in ("", None):
        return

    target_separator_col = target_col_num + 1

    if target_ws.cell(
        row=target_header_row,
        column=target_separator_col,
    ).value not in ("", None):
        target_ws.insert_cols(target_separator_col)

    copy_column_format_from_source(
        source_ws,
        target_ws,
        source_separator_col,
        target_separator_col,
        source_header_row,
        target_header_row,
    )
