import { useEffect, useMemo, useState } from "react";
import { apiFetch, errorMessage } from "./api";
import ChatInput from "./ChatInput";
import MessageList from "./MessageList";
import Notice from "./Notice";
import Sidebar from "./Sidebar";
import UploadPanel from "./UploadPanel";
import { useChat } from "./useChat";
import { useCollections } from "./useCollections";
import "./App.css";

function App({ onLogout }) {
  const {
    collections,
    currentCollection,
    setCurrentCollection,
    refreshCollections,
    deleteCollection,
    collectionsError,
  } = useCollections();
  const {
    messages,
    setMessages,
    loading,
    error: chatError,
    setError: setChatError,
    fetchHistory,
    sendMessage,
    cancel,
  } = useChat();
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState({ type: "info", message: "" });

  useEffect(() => {
    fetchHistory(currentCollection);
  }, [currentCollection, fetchHistory]);

  const currentMeta = useMemo(
    () => collections.find((item) => item.name === currentCollection),
    [collections, currentCollection]
  );

  const visibleNotice = (chatError || collectionsError)
    ? { type: "error", message: chatError || collectionsError }
    : notice;

  const handleSelectCollection = async (name) => {
    setCurrentCollection(name);
    await fetchHistory(name);
  };

  const showNotice = (type, message) => {
    setNotice({ type, message });
    if (type !== "error") setChatError("");
  };

  const handleUpload = async (file) => {
    if (!file) {
      showNotice("error", "请先选择 PDF 文件");
      return false;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await apiFetch("/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await errorMessage(response, "上传失败，请检查后端是否已启动"));
      }

      const data = await response.json();
      await refreshCollections();
      if (data.collection) {
        await handleSelectCollection(data.collection);
      }
      showNotice("success", `${data.message}，共切分为 ${data.chunk_count} 个文本块`);
      return true;
    } catch (err) {
      showNotice("error", err.message || "上传失败：网络错误或后端未响应");
      return false;
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteCollection = async (name) => {
    if (!window.confirm(`确定删除知识库「${name}」？此操作不可恢复。`)) return;
    try {
      await deleteCollection(name);
      if (currentCollection === name) {
        setCurrentCollection("");
        setMessages([]);
      }
      showNotice("success", `已删除知识库「${name}」`);
    } catch (err) {
      showNotice("error", err.message || "删除失败");
    }
  };

  const handleClearChat = async () => {
    if (!window.confirm("确定清空当前对话？")) return;
    try {
      const response = await apiFetch(
        `/history?collection=${encodeURIComponent(currentCollection)}`,
        { method: "DELETE" }
      );
      if (!response.ok) throw new Error(await errorMessage(response, "清空失败"));
      setMessages([]);
      showNotice("success", "对话已清空");
    } catch (err) {
      showNotice("error", err.message || "清空失败");
    }
  };

  return (
    <div className="app-shell">
      <Sidebar
        collections={collections}
        currentCollection={currentCollection}
        onSelectCollection={handleSelectCollection}
        onDeleteCollection={handleDeleteCollection}
        onLogout={onLogout}
      />

      <main className="chat-shell">
        <header className={`chat-header ${currentCollection ? "rag" : ""}`}>
          <span>
            {currentCollection
              ? `当前知识库：${currentCollection}${
                  currentMeta ? `（${currentMeta.chunk_count} 个文本块）` : ""
                }`
              : "普通聊天模式（不检索文档）"}
          </span>
          {messages.length > 0 && (
            <button className="light-button" type="button" onClick={handleClearChat}>
              清空对话
            </button>
          )}
        </header>

        <Notice
          type={visibleNotice.type}
          message={visibleNotice.message}
          onClose={() => setNotice({ type: "info", message: "" })}
        />

        <MessageList
          messages={messages}
          loading={loading}
          currentCollection={currentCollection}
          hasCollections={collections.length > 0}
        />

        <footer className="composer">
          <UploadPanel uploading={uploading} onUpload={handleUpload} />
          <ChatInput
            currentCollection={currentCollection}
            loading={loading}
            onSend={(value) => sendMessage(value, currentCollection)}
            onCancel={cancel}
          />
        </footer>
      </main>
    </div>
  );
}

export default App;
