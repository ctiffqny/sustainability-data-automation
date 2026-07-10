export default function PreviewTable({
  rows,
  inconsistencies = [],
  newColumns = [],
}) {
  if (!rows || rows.length === 0) {
    return (
      <section className="preview-section">
        <h2>Excel Layout Preview</h2>
        <p>No transferred rows to preview.</p>
      </section>
    );
  }

  const normalizeColumn = (value) =>
  String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");

    const newColumnNames = new Set(
    newColumns.map(normalizeColumn)
    );

  const columns = Array.from(
    new Set(
      rows.flatMap((row) => Object.keys(row.values ?? {}))
    )
  );

  const inconsistencyCells = new Set(
    inconsistencies
      .map((item) => item.target_cell)
      .filter(Boolean)
  );

  function formatPeriod(period) {
    const date = new Date(period);

    if (Number.isNaN(date.getTime())) {
      return period;
    }

    return date.toLocaleDateString("en-GB", {
      month: "short",
      year: "2-digit",
    });
  }

  function formatValue(value) {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "";
    }

    if (typeof value === "number") {
      return value.toLocaleString("en-US", {
        maximumFractionDigits: 2,
      });
    }

    return value;
  }

  function isNumeric(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function isRoundingUpdate(cell) {
    if (!cell) {
      return false;
    }

    if (cell.status === "rounding_update") {
      return true;
    }

    const oldValue = cell.old_value;
    const newValue = cell.new_value;

    if (!isNumeric(oldValue) || !isNumeric(newValue)) {
      return false;
    }

    const difference = Math.abs(oldValue - newValue);

    return difference > 0.000001 && difference < 1;
  }

  function isInconsistency(cell) {
    if (!cell) {
      return false;
    }

    return (
      cell.status === "inconsistency_not_overwritten" ||
      inconsistencyCells.has(cell.cell)
    );
  }

  function getCellClass(row, column, cell) {
    if (isInconsistency(cell)) {
        return "cell-inconsistency";
    }

    if (
        row.is_new_row ||
        newColumnNames.has(normalizeColumn(column))
    ) {
        return "cell-new-row";
    }

    if (isRoundingUpdate(cell)) {
        return "cell-rounding-update";
    }

    return "";
    }

  function getRowLabel(row) {
    if (row.row_status === "added") {
      return "New row added";
    }

    if (row.row_status === "placeholder_filled") {
      return "Existing placeholder row filled";
    }

    return "Existing row";
  }

  return (
    <section className="preview-section">
      <div className="preview-heading">
        <div>
          <h2>Excel Layout Preview</h2>

          <p>
            This shows how the transferred data will appear before
            changes are applied.
          </p>
        </div>

        <div className="preview-legend">
          <span>
            <i className="legend-box legend-new-row" />
            New or placeholder row
          </span>

          <span>
            <i className="legend-box legend-rounding" />
            Rounding update
          </span>

          <span>
            <i className="legend-box legend-inconsistency" />
            Inconsistency
          </span>
        </div>
      </div>

      <div className="excel-preview-scroll">
        <table className="excel-preview-table">
          <thead>
            <tr>
              <th>Period</th>

              {columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.map((row) => (
              <tr
                key={`${row.period}-${row.target_row}`}
                className={row.is_new_row ? "new-row" : ""}
              >
                <td title={getRowLabel(row)}>
                  {formatPeriod(row.period)}
                </td>

                {columns.map((column) => {
                  const cell = row.values?.[column];

                  return (
                    <td
                      key={column}
                      className={getCellClass(row, column, cell)}
                      title={
                        cell
                          ? `${cell.cell} | ${cell.status}`
                          : "No transferred value"
                      }
                    >
                      {formatValue(cell?.final_value)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}