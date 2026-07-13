import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function ApplyPanel({ previewResult }) {
  const [outputMode, setOutputMode] = useState("duplicate");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [applyResult, setApplyResult] = useState(null);

  /*
   * Clear an old Apply result whenever the user generates
   * a different preview.
   */
  useEffect(() => {
    setOutputMode("duplicate");
    setErrorMessage("");
    setApplyResult(null);
  }, [previewResult?.run_id]);

  async function handleApply() {
    if (
      !previewResult?.category ||
      !previewResult?.source_path ||
      !previewResult?.target_path
    ) {
      setErrorMessage(
        "The preview is missing the saved source or target file path. Generate the preview again."
      );
      return;
    }

    /*
     * Extra confirmation for the destructive-looking option.
     */
    if (outputMode === "amend") {
      const confirmed = window.confirm(
        "You selected “Amend master copy”. This may replace the master workbook with the reviewed changes.\n\nContinue?"
      );

      if (!confirmed) {
        return;
      }
    }

    setLoading(true);
    setErrorMessage("");
    setApplyResult(null);

    try {
      const formData = new FormData();

      formData.append("category", previewResult.category);
      formData.append("source_path", previewResult.source_path);
      formData.append("target_path", previewResult.target_path);
      formData.append("output_mode", outputMode);

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
      <div className="apply-panel-heading">
        <div>
          <h2>Apply Changes</h2>

          <p>
            Choose how the reviewed changes should be saved.
          </p>
        </div>
      </div>

      <fieldset
        className="output-mode-options"
        disabled={loading}
      >
        <legend>Output option</legend>

        <label
          className={`output-mode-card ${
            outputMode === "duplicate"
              ? "output-mode-card-selected"
              : ""
          }`}
        >
          <input
            type="radio"
            name="output-mode"
            value="duplicate"
            checked={outputMode === "duplicate"}
            onChange={(event) =>
              setOutputMode(event.target.value)
            }
          />

          <span className="output-mode-content">
            <strong>
              Duplicate new workbook
            </strong>

            <small>
              Keep the uploaded target unchanged and create a
              separate workbook containing the reviewed changes.
            </small>
          </span>
        </label>

        <label
          className={`output-mode-card output-mode-card-warning ${
            outputMode === "amend"
              ? "output-mode-card-selected"
              : ""
          }`}
        >
          <input
            type="radio"
            name="output-mode"
            value="amend"
            checked={outputMode === "amend"}
            disabled
          />

          <span className="output-mode-content">
            <strong>Amend master copy</strong>

            <small>
              Apply the reviewed changes to the selected master
              workbook. You will be asked to confirm first. COMING SOON
            </small>
          </span>
        </label>
      </fieldset>

      {outputMode === "amend" && !applyResult && (
        <div className="apply-warning" role="alert">
          <strong>Review carefully.</strong> The amend option is
          intended for updating the master workbook.
        </div>
      )}

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
            : outputMode === "amend"
              ? "Confirm and Amend Master Copy"
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