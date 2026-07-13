import { useState } from "react";
import axios from "axios";

export default function UploadForm({ onPreview }) {
  const [category, setCategory] = useState("electricity");
  const [sourceFile, setSourceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  async function handlePreview(event) {
  event.preventDefault();

  if (!(sourceFile instanceof File) || !(targetFile instanceof File)) {
    setErrorMessage("Please select both workbooks again.");
    return;
  }

  setLoading(true);
  setErrorMessage("");
  onPreview(null);

  try {
    const formData = new FormData();

    formData.append("category", category);

    formData.append(
      "source_file",
      sourceFile,
      sourceFile.name
    );

    formData.append(
      "target_file",
      targetFile,
      targetFile.name
    );

    console.log({
      sourceFile,
      sourceIsFile: sourceFile instanceof File,
      targetFile,
      targetIsFile: targetFile instanceof File,
    });

    const response = await axios.post(
      "http://127.0.0.1:8000/preview",
      formData
    );

    if (response.data?.status === "error") {
      setErrorMessage(
        response.data.message ?? "Preview failed."
      );
      return;
    }

    onPreview(response.data);
  } catch (error) {
    console.error("Preview failed:", error);

    const detail = error.response?.data?.detail;

    if (detail) {
      setErrorMessage(
        typeof detail === "string"
          ? detail
          : detail
              .map((item) => item.msg)
              .join(", ")
      );
    } else if (error.response) {
      setErrorMessage(
        `Backend error: ${error.response.status}`
      );
    } else {
      setErrorMessage(
        "Could not connect to the backend."
      );
    }
  } finally {
    setLoading(false);
  }
}

  return (
    <form
      className="upload-form"
      onSubmit={handlePreview}
    >
      <h2>Upload Files</h2>

      <div className="form-field">
        <label htmlFor="category">Category</label>

        <select
          id="category"
          value={category}
          onChange={(event) =>
            setCategory(event.target.value)
          }
        >
          <option value="electricity">
            Electricity
          </option>

          <option value="recyclable_wastes">
            Recyclable Wastes
          </option>
        </select>
      </div>

      <div className="form-field">
        <label htmlFor="source-file">
          Source Workbook
        </label>

        <input
          id="source-file"
          type="file"
          accept=".xlsx,.xlsm"
          onChange={(event) =>
            setSourceFile(event.target.files?.[0] ?? null)
          }
        />

        {sourceFile && (
          <small>{sourceFile.name}</small>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="target-file">
          Target Workbook
        </label>

        <input
          id="target-file"
          type="file"
          accept=".xlsx,.xlsm"
          onChange={(event) =>
            setTargetFile(event.target.files?.[0] ?? null)
          }
        />

        {targetFile && (
          <small>{targetFile.name}</small>
        )}
      </div>

      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
      >
        {loading
          ? "Generating preview..."
          : "Preview Changes"}
      </button>
    </form>
  );
}