import { useState } from "react";
import axios from "axios";

export default function FoodWasteUpload({ onResult }) {
  const [month, setMonth] = useState("Apr-26");
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();

    if (files.length === 0) {
      alert("Please choose at least one PDF.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();

      formData.append("month", month);

      files.forEach((file) => {
        formData.append("pdf_files", file);
      });

      const response = await axios.post(
        "http://127.0.0.1:8000/food-waste-pdf/multiple",
        formData,
        {
            timeout: 120000,
        }
      );

      onResult(response.data);
    } catch (err) {
      console.error(err);
      alert("Upload failed.");
    }

    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Food Waste PDFs</h2>

      <input
        value={month}
        onChange={(e) => setMonth(e.target.value)}
        placeholder="Apr-26"
      />

      <input
        type="file"
        accept=".pdf"
        multiple
        onChange={(e) =>
          setFiles(Array.from(e.target.files))
        }
      />

      <p>{files.length} PDF(s) selected</p>

      <button disabled={loading}>
        {loading ? "Processing..." : "Process PDFs"}
      </button>
    </form>
  );
}