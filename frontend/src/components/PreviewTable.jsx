export default function PreviewTable({ rows }) {
  if (!rows || rows.length === 0) {
    return <p>No updated rows to preview.</p>;
  }

  return (
    <div>
      <h2>Transfer Preview</h2>

      <table className="preview-table">
        <thead>
          <tr>
            <th>Period</th>
            <th>Target Row</th>
            <th>Column</th>
            <th>Cell</th>
            <th>Old Value</th>
            <th>New Value</th>
            <th>Final Value</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {rows.flatMap((row) =>
            Object.entries(row.values).map(([columnName, value]) => (
              <tr key={`${row.period}-${columnName}`}>
                <td>{new Date(row.period).toLocaleDateString("en-GB", {
                  month: "short",
                  year: "2-digit",
                })}</td>
                <td>{row.target_row}</td>
                <td>{columnName}</td>
                <td>{value.cell}</td>
                <td>{value.old_value ?? ""}</td>
                <td>{value.new_value ?? ""}</td>
                <td>{value.final_value ?? ""}</td>
                <td>{value.status}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}