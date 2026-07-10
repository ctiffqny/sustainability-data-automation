import { useState } from "react";
import UploadForm from "./components/UploadForm";
import ReviewDashboard from "./components/ReviewDashboard";
import "./App.css";

function App() {
  const [previewResult, setPreviewResult] = useState(null);

  return (
    <main className="app">
      <h1>Sustainability Data Automation</h1>

      <UploadForm onPreview={setPreviewResult} />

      <hr className="page-divider" />

      {!previewResult ? (
        <p className="empty-message">No preview generated.</p>
      ) : (
        <ReviewDashboard previewResult={previewResult} />
      )}
    </main>
  );
}

export default App;