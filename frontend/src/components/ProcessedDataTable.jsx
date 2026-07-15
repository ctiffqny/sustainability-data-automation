export default function ProcessedDataTable({
  rows = [],
  title = "Processed Data",
  description = "",
  category,
}) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return (
      <section className="preview-section">
        <h2>{title}</h2>
        <p>No processed data is available.</p>
      </section>
    );
  }

  const isFoodWaste = category === "food_waste";

  const discoveredColumns = Array.from(
    new Set(
      rows.flatMap((row) =>
        Object.keys(row.values ?? {})
      )
    )
  );

  const yearlyColumn =
    discoveredColumns.find((column) =>
      [
        "Yearly Total (kg)",
        "Yearly Total Waste Generated",
      ].includes(column)
    ) ?? "Yearly Total (kg)";

  const columns = isFoodWaste
    ? [
        "Total (kg)",
        yearlyColumn,
        ...discoveredColumns.filter(
          (column) =>
            column !== "Total (kg)" &&
            column !== "Yearly Total (kg)" &&
            column !== "Yearly Total Waste Generated"
        ),
      ]
    : discoveredColumns;

  function formatPeriod(period) {
    if (
      period === null ||
      period === undefined ||
      period === ""
    ) {
      return "";
    }

    const text = String(period).trim();

    const match = text.match(
      /^([A-Za-z]{3,9})[\s-](\d{2}|\d{4})$/
    );

    if (match) {
      const month =
        match[1].charAt(0).toUpperCase() +
        match[1].slice(1, 3).toLowerCase();

      const year =
        match[2].length === 4
          ? match[2].slice(-2)
          : match[2];

      return `${month} ${year}`;
    }

    const date = new Date(period);

    if (!Number.isNaN(date.getTime())) {
      return date.toLocaleDateString("en-GB", {
        month: "short",
        year: "2-digit",
      });
    }

    return text;
  }

  function formatValue(value) {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "";
    }

    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {
      return value.toLocaleString("en-US", {
        maximumFractionDigits: 2,
      });
    }

    return String(value);
  }

  function isYearlyColumn(column) {
    return (
      column === "Yearly Total (kg)" ||
      column === "Yearly Total Waste Generated"
    );
  }

  return (
    <section
      className={
        isFoodWaste
          ? "preview-section processed-food-waste-section"
          : "preview-section"
      }
    >
      <div className="preview-heading">
        <div>
          <h2>{title}</h2>

          {description && (
            <p>{description}</p>
          )}
        </div>
      </div>

      <div
        className={
          isFoodWaste
            ? "processed-food-waste-table-wrapper"
            : "excel-preview-scroll"
        }
      >
        <table
          className={
            isFoodWaste
              ? "excel-preview-table processed-food-waste-table"
              : "excel-preview-table"
          }
        >
          <thead>
            <tr>
              <th>Period</th>

              {columns.map((column) => {
                const grayYearlyColumn =
                  isFoodWaste &&
                  isYearlyColumn(column);

                return (
                  <th
                    key={column}
                    className={
                      grayYearlyColumn
                        ? "processed-yearly-header"
                        : ""
                    }
                  >
                    {column}
                  </th>
                );
              })}
            </tr>
          </thead>

          <tbody>
            {rows.map((row, index) => (
              <tr
                key={`${row.period}-${row.target_row}-${index}`}
              >
                <td>
                  {formatPeriod(row.period)}
                </td>

                {columns.map((column) => {
                  const value =
                    row.values?.[column]?.final_value;

                  const isEmpty =
                    value === null ||
                    value === undefined ||
                    value === "";

                  const grayYearlyColumn =
                    isFoodWaste &&
                    isYearlyColumn(column);

                  return (
                    <td
                      key={column}
                      className={
                        grayYearlyColumn
                          ? "processed-yearly-cell"
                          : ""
                      }
                      title={
                        grayYearlyColumn && isEmpty
                          ? "Yearly total is calculated only in June."
                          : undefined
                      }
                    >
                      {grayYearlyColumn && isEmpty
                        ? "—"
                        : formatValue(value)}
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