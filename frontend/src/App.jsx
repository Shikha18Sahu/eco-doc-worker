import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const STATUS_STYLES = {
  approved: "bg-green-100 text-green-800 border-green-300",
  escalated: "bg-red-100 text-red-800 border-red-300",
  awaiting_user_input: "bg-yellow-100 text-yellow-800 border-yellow-300",
  failed: "bg-red-100 text-red-800 border-red-300",
};

function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || "bg-gray-100 text-gray-800 border-gray-300";
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${style}`}>
      {status?.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editedFields, setEditedFields] = useState({});

  const startWorkflow = async () => {
    if (!file) {
      alert("Please select an image file first");
      return;
    }
    setLoading(true);
    setResult(null);
    setEditedFields({});
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/workflow/start`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: String(err) });
    } finally {
      setLoading(false);
    }
  };

  const resumeWorkflow = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/workflow/${result.workflow_id}/resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ additional_fields: editedFields }),
      });
      const data = await res.json();
      setResult(data);
      setEditedFields({});
    } catch (err) {
      setResult({ error: String(err) });
    } finally {
      setLoading(false);
    }
  };

  const documentType = result?.structured_data?._document_type;
  const visibleFields = result?.structured_data
    ? Object.entries(result.structured_data).filter(([k]) => !k.startsWith("_"))
    : [];

  const missingFieldNames = visibleFields
    .filter(([, value]) => !value)
    .map(([key]) => key);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <h1 className="text-2xl font-bold mb-1">Autonomous Document Worker</h1>
      <p className="text-gray-500 mb-6 text-sm">
        Upload a document (resume, onboarding form, admission form, or KYC form)
      </p>

      <div className="bg-white rounded-lg shadow p-6 w-full max-w-xl mb-6">
        <input
          type="file"
          accept="image/*"
          className="mb-4 block"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50 w-full"
          onClick={startWorkflow}
          disabled={loading}
        >
          {loading ? "Processing..." : "Start Workflow"}
        </button>
      </div>

      {result && !result.error && (
        <div className="bg-white rounded-lg shadow p-6 w-full max-w-xl space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400 font-mono">{result.workflow_id}</span>
            <StatusBadge status={result.status} />
          </div>

          {documentType && (
            <div>
              <span className="text-sm text-gray-500">Document Type: </span>
              <span className="font-semibold capitalize">
                {documentType.replace(/_/g, " ")}
              </span>
            </div>
          )}

          <div>
            <span className="text-sm text-gray-500">Confidence: </span>
            <span className="font-semibold">
              {(result.confidence * 100).toFixed(0)}%
            </span>
          </div>

          {visibleFields.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Extracted Fields</h3>
              <div className="space-y-1">
                {visibleFields.map(([key, value]) => (
                  <div key={key} className="flex text-sm border-b border-gray-100 py-1">
                    <span className="w-1/3 text-gray-500 capitalize">
                      {key.replace(/_/g, " ")}
                    </span>
                    <span className={`flex-1 ${value ? "text-gray-900" : "text-red-400 italic"}`}>
                      {value || "missing"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.validation_errors?.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded p-3">
              <h3 className="text-sm font-semibold text-red-700 mb-1">Validation Issues</h3>
              <ul className="text-sm text-red-600 list-disc list-inside">
                {result.validation_errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          {result.next_action === "ask_user" && missingFieldNames.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded p-3 space-y-2">
              <h3 className="text-sm font-semibold text-blue-700">
                Please provide the missing information
              </h3>
              {missingFieldNames.map((field) => (
                <input
                  key={field}
                  placeholder={field.replace(/_/g, " ")}
                  className="border rounded px-2 py-1 w-full text-sm"
                  value={editedFields[field] || ""}
                  onChange={(e) =>
                    setEditedFields({ ...editedFields, [field]: e.target.value })
                  }
                />
              ))}
              <button
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm disabled:opacity-50 w-full"
                onClick={resumeWorkflow}
                disabled={loading}
              >
                {loading ? "Submitting..." : "Submit and Re-check"}
              </button>
            </div>
          )}

          {result.human_review_required && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
              ⚠️ This document requires human review before it can be finalized.
            </div>
          )}
        </div>
      )}

      {result?.error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 w-full max-w-xl text-red-700 text-sm">
          {result.error}
        </div>
      )}
    </div>
  );
}

export default App;