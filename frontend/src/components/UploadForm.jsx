import { useState } from "react";
import axios from "axios";

function UploadForm({ onPreview }) {
  const [category, setCategory] = useState("electricity");
  const [sourceFile, setSourceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);

  async function handlePreview() {
    if (!sourceFile || !targetFile) {
        alert("Please select both workbooks.");
        return;
    }

    try {
        const formData = new FormData();

        formData.append("category", category);
        formData.append("source_file", sourceFile);
        formData.append("target_file", targetFile);

        const response = await axios.post(
        "http://127.0.0.1:8000/preview",
        formData
        );

        onPreview(response.data);

    } catch (error) {
        console.error(error);

        if (error.response) {
        console.log(error.response.data);
        alert(`Backend Error: ${error.response.status}`);
        } else {
        alert("Could not connect to backend.");
        }
    }
    }
  return (
    <div>
      <h2>Upload Files</h2>

      <div>
        <label>Category</label>
        <br />
        <select
          value={category}
          onChange={(event) => setCategory(event.target.value)}
        >
          <option value="electricity">Electricity</option>
          <option value="recyclable_wastes">Recyclable Wastes</option>
        </select>
      </div>

      <br />

      <div>
        <label>Source Workbook</label>
        <br />
        <input
          type="file"
          accept=".xlsx,.xlsm,.xls"
          onChange={(event) => setSourceFile(event.target.files[0])}
        />
      </div>

      <br />

      <div>
        <label>Target Workbook</label>
        <br />
        <input
          type="file"
          accept=".xlsx,.xlsm,.xls"
          onChange={(event) => setTargetFile(event.target.files[0])}
        />
      </div>

      <br />

      <button onClick={handlePreview}>Preview Changes</button>
    </div>
  );
}

export default UploadForm;