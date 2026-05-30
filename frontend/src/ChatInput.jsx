import { useState } from "react";

export default function ChatInput({ currentCollection, loading, onSend, onCancel }) {
  const [input, setInput] = useState("");

  const submit = async () => {
    const sent = await onSend(input);
    if (sent) setInput("");
  };

  return (
    <div className="chat-input-row">
      <textarea
        value={input}
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            if (!loading) submit();
          }
        }}
        disabled={loading}
        placeholder={
          currentCollection
            ? `向「${currentCollection}」提问，Shift+Enter 换行...`
            : "普通聊天，Shift+Enter 换行..."
        }
        rows={2}
      />
      {loading ? (
        <button className="secondary-button" type="button" onClick={onCancel}>
          停止
        </button>
      ) : (
        <button className="primary-button" type="button" onClick={submit}>
          发送
        </button>
      )}
    </div>
  );
}
