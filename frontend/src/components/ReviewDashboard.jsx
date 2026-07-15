import PreviewTable from "./PreviewTable";
import InconsistencyTable from "./InconsistencyTable";
import ApplyPanel from "./ApplyPanel";
import ProcessedDataTable from "./ProcessedDataTable";

export default function ReviewDashboard({ previewResult }) {
  /*
   * Supports both response shapes:
   *
   * 1. Direct:
   *    {
   *      status: "success",
   *      category: "electricity",
   *      updated_rows: [...],
   *      inconsistencies: [...],
   *      new_columns: [...],
   *      skipped_columns: [...]
   *    }
   *
   * 2. Wrapped:
   *    {
   *      status: "success",
   *      category: "electricity",
   *      preview: {
   *        updated_rows: [...],
   *        inconsistencies: [...],
   *        new_columns: [...],
   *        skipped_columns: [...]
   *      }
   *    }
   */

  const preview = previewResult?.preview ?? previewResult ?? {};

  const updatedRows = Array.isArray(preview.updated_rows)
    ? preview.updated_rows
    : [];

  const processedRows = Array.isArray(
    preview.processed_rows
  )
    ? preview.processed_rows
    : [];

  const inconsistencies = Array.isArray(preview.inconsistencies)
    ? preview.inconsistencies
    : [];

  const newColumns = Array.isArray(preview.new_columns)
    ? preview.new_columns
    : [];

  const skippedColumns = Array.isArray(preview.skipped_columns)
    ? preview.skipped_columns
    : [];

  const status =
    previewResult?.status ??
    preview.status ??
    "success";

  const category =
    previewResult?.category ??
    preview.category ??
    "Unknown";

  /*
   * Use a backend-provided reviewed-row count when available.
   * Otherwise, fall back to the number of updated rows.
   */
  const rowsReviewed =
    preview.rows_reviewed ??
    previewResult?.rows_reviewed ??
    updatedRows.length;

  const formatValue = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "None";
    }

    if (Array.isArray(value)) {
      return value.length > 0
        ? value.join(", ")
        : "None";
    }

    return String(value);
  };

  return (
    <section className="review-dashboard">
      <section className="summary-card">
        <h2>Preview Summary</h2>

        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">
              Status
            </span>

            <span className="summary-value">
              {formatValue(status)}
            </span>
          </div>

          <div className="summary-item">
            <span className="summary-label">
              Category
            </span>

            <span className="summary-value">
              {formatValue(category)}
            </span>
          </div>

          <div className="summary-item">
            <span className="summary-label">
              Rows reviewed
            </span>

            <span className="summary-value">
              {formatValue(rowsReviewed)}
            </span>
          </div>

          <div className="summary-item">
            <span className="summary-label">
              Inconsistencies
            </span>

            <span className="summary-value">
              {inconsistencies.length}
            </span>
          </div>

          <div className="summary-item">
            <span className="summary-label">
              New columns
            </span>

            <span className="summary-value">
              {formatValue(newColumns)}
            </span>
          </div>

          <div className="summary-item">
            <span className="summary-label">
              Skipped columns
            </span>

            <span className="summary-value summary-warning">
              {formatValue(skippedColumns)}
            </span>
          </div>
        </div>
      </section>

      <PreviewTable
        rows={updatedRows}
        inconsistencies={inconsistencies}
        newColumns={newColumns}
        category={category}
      />

      {processedRows.length > 0 && (
        <ProcessedDataTable
            rows={processedRows}
            category={category}
            title={
              category === "recyclable_wastes"
                ? "Processed Solid Waste Data"
                : category === "food_waste"
                  ? "Processed Food Waste Data"
                  : "Processed Data"
            }
            description={
              category === "recyclable_wastes"
                ? "These values were calculated by the backend using the rules configured in the recyclable waste YAML file. Yearly Total Waste Generated is calculated only every June."
                : category === "food_waste"
                  ? "Total (kg) is calculated from the location columns for the selected month. Yearly Total (kg) is a rolling 12-month total and is calculated only every June."
                  : "These values were calculated by the backend."
            }
        />
        )}

      <ApplyPanel
        previewResult={previewResult}
      />

      <InconsistencyTable
        inconsistencies={inconsistencies}
      />
    </section>
  );
}