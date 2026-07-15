import { useState } from "react";
import axios from "axios";

const EXCEL_CATEGORIES = [
  "electricity",
  "recyclable_wastes",
];

export default function UploadForm({ onPreview }) {
  const [category, setCategory] = useState("electricity");

  const [sourceFile, setSourceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);

  const [pdfFiles, setPdfFiles] = useState([]);
  const currentDate = new Date();

  const defaultMonth = `${currentDate.toLocaleString("en-US", {
    month: "short",
  })}-${String(currentDate.getFullYear()).slice(-2)}`;

  const [month, setMonth] = useState(defaultMonth);

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const isFoodWaste = category === "food_waste";
  const isExcelCategory =
    EXCEL_CATEGORIES.includes(category);

  function resetSelectedFiles(nextCategory) {
    setSourceFile(null);
    setTargetFile(null);
    setPdfFiles([]);
    setErrorMessage("");
    onPreview(null);

    setCategory(nextCategory);
  }

  function validateExcelUpload() {
    if (!(sourceFile instanceof File)) {
      return "Please select a source workbook.";
    }

    if (!(targetFile instanceof File)) {
      return "Please select a target workbook.";
    }

    return null;
  }

  function validateFoodWasteUpload() {
    if (!month.trim()) {
      return "Please enter a month such as Apr-26.";
    }

    if (pdfFiles.length === 0) {
      return "Please select at least one PDF.";
    }

    if (!(targetFile instanceof File)) {
      return "Please select the target workbook.";
    }

    return null;
  }

  async function submitExcelPreview() {
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

    return axios.post(
      "http://127.0.0.1:8000/preview",
      formData
    );
  }

  async function submitFoodWastePDFs() {
    const formData = new FormData();

    formData.append("category", "food_waste");
    formData.append("month", month.trim());

    pdfFiles.forEach((file) => {
      formData.append(
        "source_files",
        file,
        file.name
      );
    });

    formData.append(
      "target_file",
      targetFile,
      targetFile.name
    );

    return axios.post(
      "http://127.0.0.1:8000/preview",
      formData
    );
  }

  async function handlePreview(event) {
    event.preventDefault();

    const validationError = isFoodWaste
      ? validateFoodWasteUpload()
      : validateExcelUpload();

    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    setLoading(true);
    setErrorMessage("");
    onPreview(null);

    try {
      const response = isFoodWaste
        ? await submitFoodWastePDFs()
        : await submitExcelPreview();

      if (response.data?.status === "error") {
        setErrorMessage(
          response.data.message ??
            "Processing failed."
        );
        return;
      }

      onPreview({
        ...response.data,
        category,
      });
  } catch (error) {
    console.error("Processing failed:", error);

    if (error.code === "ECONNABORTED") {
      setErrorMessage(
        "The request timed out. Check the backend terminal."
      );
    } else if (error.response?.data?.detail) {
      const detail = error.response.data.detail;

      setErrorMessage(
        typeof detail === "string"
          ? detail
          : JSON.stringify(detail)
      );
    } else if (error.response) {
      setErrorMessage(
        `Backend error ${error.response.status}`
      );
    } else {
      setErrorMessage(
        `Could not connect to the backend: ${error.message}`
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
        <label htmlFor="category">
          Category
        </label>

        <select
          id="category"
          value={category}
          onChange={(event) =>
            resetSelectedFiles(
              event.target.value
            )
          }
        >
          <option value="electricity">
            Electricity
          </option>

          <option value="recyclable_wastes">
            Recyclable Wastes
          </option>

          <option value="food_waste">
            Food Waste PDFs
          </option>
        </select>
      </div>

      {isExcelCategory && (
        <>
          <div className="form-field">
            <label htmlFor="source-file">
              Source Workbook
            </label>

            <input
              id="source-file"
              type="file"
              accept=".xlsx,.xlsm"
              onChange={(event) =>
                setSourceFile(
                  event.target.files?.[0] ??
                    null
                )
              }
            />

            {sourceFile && (
              <small>
                {sourceFile.name}
              </small>
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
                setTargetFile(
                  event.target.files?.[0] ??
                    null
                )
              }
            />

            {targetFile && (
              <small>
                {targetFile.name}
              </small>
            )}
          </div>
        </>
      )}

      {isFoodWaste && (
  <>
    <div className="form-field">
      <label htmlFor="food-waste-month">
        Collection Month
      </label>

      <input
        id="food-waste-month"
        type="text"
        value={month}
        placeholder="e.g. Apr-26"
        onChange={(event) =>
          setMonth(event.target.value)
        }
      />
    </div>

    <div className="form-field">
      <label htmlFor="food-waste-pdfs">
        Source Food Waste PDFs
      </label>

      <input
        id="food-waste-pdfs"
        type="file"
        accept=".pdf,application/pdf"
        multiple
        onChange={(event) =>
          setPdfFiles(
            Array.from(
              event.target.files ?? []
            )
          )
        }
      />

      <small>
        {pdfFiles.length} PDF(s) selected
      </small>
    </div>

    <div className="form-field">
      <label htmlFor="food-waste-target">
        Target Workbook
      </label>

      <input
        id="food-waste-target"
        type="file"
        accept=".xlsx,.xlsm"
        onChange={(event) =>
          setTargetFile(
            event.target.files?.[0] ??
              null
          )
        }
      />

      {targetFile && (
        <small>{targetFile.name}</small>
      )}
    </div>
  </>
)}

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
          ? isFoodWaste
            ? "Processing PDFs..."
            : "Generating preview..."
          : isFoodWaste
            ? "Process PDFs"
            : "Preview Changes"}
      </button>
    </form>
  );
}