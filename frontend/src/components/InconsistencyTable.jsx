export default function InconsistencyTable({ inconsistencies }) {
  if (!inconsistencies || inconsistencies.length === 0) {
    return <p>No inconsistencies found.</p>;
  }

  return (
    <div>
      <h2>Inconsistencies</h2>
      <p>These cells were not overwritten.</p>

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
    </div>
  );
}