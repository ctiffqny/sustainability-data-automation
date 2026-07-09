import { useState } from "react";
import UploadForm from "./components/UploadForm";
import "./App.css";

function ExcelLayoutPreview({ rows }) {
  if (!rows || rows.length === 0) {
    return <p>No rows to preview.</p>;
  }

  const columns = Array.from(
    new Set(rows.flatMap((row) => Object.keys(row.values)))
  );

  function formatPeriod(period) {
    return new Date(period).toLocaleDateString("en-GB", {
      month: "short",
      year: "2-digit",
    });
  }

  function formatValue(value) {
    if (value === null || value === undefined || value === "") return "";

    if (typeof value === "number") {
      return value.toLocaleString("en-US", {
        maximumFractionDigits: 2,
      });
    }

    return value;
  }

  return (
    <section>
      <h2>Excel Layout Preview</h2>
      <p>This shows how the transferred rows will look before applying changes.</p>

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
              <tr key={row.period}>
                <td>{formatPeriod(row.period)}</td>

                {columns.map((column) => {
                  const cell = row.values[column];

                  return (
                    <td
                      key={column}
                      className={
                        cell?.status === "inconsistency_not_overwritten"
                          ? "cell-inconsistency"
                          : cell?.status === "blank_source_skipped"
                          ? "cell-skipped"
                          : ""
                      }
                      title={cell ? `${cell.cell} | ${cell.status}` : ""}
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

function InconsistencyTable({ inconsistencies }) {
  return (
    <section>
      <h2>Inconsistencies</h2>

      {!inconsistencies || inconsistencies.length === 0 ? (
        <p>No inconsistencies found.</p>
      ) : (
        <table className="preview-table">
          <thead>
            <tr>
              <th>Period</th>
              <th>Column</th>
              <th>Target Cell</th>
              <th>Source Cell</th>
              <th>Existing Target Value</th>
              <th>New Source Value</th>
            </tr>
          </thead>

          <tbody>
            {inconsistencies.map((item, index) => (
              <tr key={index}>
                <td>{item.period}</td>
                <td>{item.column}</td>
                <td>{item.target_cell}</td>
                <td>{item.source_cell}</td>
                <td>{item.existing_target_value}</td>
                <td>{item.new_source_value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

function App() {
  const [previewResult, setPreviewResult] = useState(null);

  return (
    <div className="app">
      <h1>Sustainability Data Automation</h1>

      <UploadForm onPreview={setPreviewResult} />

      <hr />

      {!previewResult ? (
        <p>No preview generated.</p>
      ) : (
        <>
          <section className="summary-card">
            <h2>Preview Summary</h2>
            <p><strong>Status:</strong> {previewResult.status}</p>
            <p><strong>Category:</strong> {previewResult.category}</p>
            <p><strong>Config:</strong> {previewResult.config_used}</p>
          </section>

          <InconsistencyTable inconsistencies={previewResult.inconsistencies} />
          <ExcelLayoutPreview rows={previewResult.updated_rows} />
        </>
      )}
    </div>
  );
}

export default App;