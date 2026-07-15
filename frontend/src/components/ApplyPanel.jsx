import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function ApplyPanel({ previewResult }) {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [applyResult, setApplyResult] = useState(null);

  /*
   * Clear an old Apply result whenever the user generates
   * a different preview.
   */
  useEffect(() => {
    setErrorMessage("");
    setApplyResult(null);
  }, [previewResult?.run_id]);

  async function handleApply() {
    const isFoodWaste = previewResult?.category === "food_waste";
    const hasSource = isFoodWaste
      ? Array.isArray(previewResult?.source_paths) &&
        previewResult.source_paths.length > 0
      : Boolean(previewResult?.source_path);

    if (
      !previewResult?.category ||
      !hasSource ||
      !previewResult?.target_path
    ) {
      setErrorMessage(
        "The preview is missing the saved source or target file path. Generate the preview again."
      );
      return;
    }

    setLoading(true);
    setErrorMessage("");
    setApplyResult(null);

    try {
      const formData = new FormData();

      formData.append("category", previewResult.category);
      formData.append("target_path", previewResult.target_path);

      if (previewResult.category === "food_waste") {
        previewResult.source_paths.forEach((path) => {
          formData.append("source_paths", path);
        });
        formData.append("month", previewResult.month ?? "");
      } else {
        formData.append("source_path", previewResult.source_path);
      }

      const response = await axios.post(
        `${API_BASE_URL}/apply`,
        formData
      );

      if (response.data?.status === "error") {
        setErrorMessage(
          response.data.message ?? "The changes could not be applied."
        );
        return;
      }

      setApplyResult(response.data);
    } catch (error) {
      console.error("Apply failed:", error);

      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;

        setErrorMessage(
          typeof detail === "string"
            ? detail
            : JSON.stringify(detail)
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

  function createDownloadUrl(filePath) {
    if (!filePath) {
      return "#";
    }

    const query = new URLSearchParams({
      file_path: filePath,
    });

    return `${API_BASE_URL}/download?${query.toString()}`;
  }

  const supportsHighlightedSource =
  previewResult?.category === "electricity";

  return (
    <section className="apply-panel">

      {errorMessage && (
        <div className="error-message" role="alert">
          {errorMessage}
        </div>
      )}

      {!applyResult && (
        <button
          type="button"
          className="apply-button"
          onClick={handleApply}
          disabled={loading}
        >
          {loading
            ? "Applying changes..."
              : "Create Updated Workbook"}
        </button>
      )}

      {applyResult && (
        <section
          className="apply-success"
          aria-live="polite"
        >
          <h3>Changes applied successfully</h3>

          <p>
            The reviewed {previewResult.category?.replaceAll("_", " ")} data has been processed.
            Download the generated files below.
          </p>

          <div className="download-actions">
            {applyResult.output_file && (
              <a
                className="download-button download-button-primary"
                href={createDownloadUrl(
                  applyResult.output_file
                )}
              >
                Download updated workbook
              </a>
            )}

            {supportsHighlightedSource ? (
                <a
                    className="download-button"
                    href={createDownloadUrl(
                    applyResult.highlighted_source_file
                    )}
                >
                    Download highlighted source
                </a>
                ) : (
                <button
                    type="button"
                    className="download-button"
                    disabled
                    title="Not available for Recyclable Wastes."
                >
                    Download highlighted source
                </button>
                )}
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setApplyResult(null);
              setErrorMessage("");
            }}
          >
            Apply again
          </button>
        </section>
      )}
    </section>
  );
}