import { useState } from "react";

export default function UploadPanel({ uploading, onUpload }) {
  const [file, setFile] = useState(null);

  const upload = async () => {
    const ok = await onUpload(file);
    if (ok) setFile(null);
  };

  return (
    <div className="upload-panel">
      <label>
        <span>上传 PDF</span>
        <input
          type="file"
          accept=".pdf,application/pdf"
          onChange={(event) => setFile(event.target.files[0] || null)}
        />
      </label>
      <button
        className="success-button"
        type="button"
        onClick={upload}
        disabled={uploading || !file}
      >
        {uploading ? "上传中" : "建立知识库"}
      </button>
    </div>
  );
}
