import { useRef, useState } from "react";

export default function FileDropzone({ onFileSelect, isLoading, error }) {
  const inputRef = useRef(null);
  const [selectedName, setSelectedName] = useState(null);
  const [dragging, setDragging] = useState(false);

  function handleFile(file) {
    if (!file || file.type !== "application/pdf") return;
    setSelectedName(file.name);
    onFileSelect(file);
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  }

  return (
    <div>
      <div
        className={`dropzone${dragging ? " dropzone--active" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <div style={{ fontSize: 32, marginBottom: 8 }}>📄</div>
        {selectedName
          ? <p style={{ margin: 0, fontWeight: 500 }}>{selectedName}</p>
          : <p style={{ margin: 0, color: "var(--text-muted)" }}>Drop your PDF here or click to browse</p>
        }
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      {isLoading && (
        <div className="progress-bar" style={{ marginTop: 8 }}>
          <div className="progress-fill progress-fill--animated" />
        </div>
      )}

      {error && (
        <p style={{ color: "var(--danger)", marginTop: 8, fontSize: 14 }}>{error}</p>
      )}
    </div>
  );
}
