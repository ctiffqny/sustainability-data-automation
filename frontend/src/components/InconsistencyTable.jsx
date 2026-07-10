export default function InconsistencyTable({
  inconsistencies,
}) {
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

  if (!inconsistencies || inconsistencies.length === 0) {
    return (
      <section className="inconsistency-section">
        <h2>Inconsistency List</h2>

        <div className="success-message">
          No inconsistencies found.
        </div>
      </section>
    );
  }

  return (
    <section className="inconsistency-section">
      <h2>Inconsistency List</h2>

      <p>
        These cells were not overwritten. The existing target values
        will be preserved.
      </p>

      <div className="table-scroll">
        <table className="inconsistency-table">
          <thead>
            <tr>
              <th>Period</th>
              <th>Column</th>
              <th>Target Cell</th>
              <th>Source Cell</th>
              <th>Existing Target Value</th>
              <th>New Source Value</th>
              <th>Difference</th>
            </tr>
          </thead>

          <tbody>
            {inconsistencies.map((item, index) => {
              const existing = item.existing_target_value;
              const incoming = item.new_source_value;

              const difference =
                typeof existing === "number" &&
                typeof incoming === "number"
                  ? incoming - existing
                  : null;

              return (
                <tr
                  key={`${item.target_cell}-${item.period}-${index}`}
                >
                  <td>{item.period}</td>
                  <td>{item.column}</td>
                  <td>{item.target_cell}</td>
                  <td>{item.source_cell}</td>
                  <td>{formatValue(existing)}</td>
                  <td>{formatValue(incoming)}</td>
                  <td>{formatValue(difference)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}