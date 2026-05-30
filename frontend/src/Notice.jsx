export default function Notice({ type = "info", message, onClose }) {
  if (!message) return null;

  return (
    <div className={`notice ${type}`} role="status">
      <span>{message}</span>
      <button type="button" onClick={onClose} aria-label="关闭提示">
        ×
      </button>
    </div>
  );
}
