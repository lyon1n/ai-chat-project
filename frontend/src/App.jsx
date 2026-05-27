import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { tomorrow } from "react-syntax-highlighter/dist/esm/styles/prism";
import { apiFetch, authHeaders, clearToken } from "./api";

function App({ username, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [collections, setCollections] = useState([]);
  const [currentCollection, setCurrentCollection] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef(null);

  const fetchCollections = async () => {
    try {
      const res = await apiFetch("/collections");
      const data = await res.json();
      setCollections(data.collections || []);
    } catch {
      setCollections([]);
    }
  };

  const fetchHistory = async (collection) => {
    try {
      const res = await apiFetch(
        `/history?collection=${encodeURIComponent(collection)}`
      );
      const data = await res.json();
      setMessages(Array.isArray(data) ? data : []);
    } catch {
      setMessages([]);
    }
  };

  useEffect(() => {
    fetchCollections();
  }, []);

  useEffect(() => {
    fetchHistory(currentCollection);
  }, [currentCollection]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const selectCollection = (name) => {
    setCurrentCollection(name);
  };

  const deleteCollection = async (name, e) => {
    e.stopPropagation();
    if (!window.confirm(`确定删除知识库「${name}」？此操作不可恢复。`)) {
      return;
    }

    const res = await apiFetch(`/collections/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });

    if (!res.ok) {
      let errMsg = "删除失败";
      try {
        const err = await res.json();
        if (err.detail) errMsg = err.detail;
      } catch {
        /* ignore */
      }
      alert(errMsg);
      return;
    }

    if (currentCollection === name) {
      setCurrentCollection("");
      setMessages([]);
    }
    await fetchCollections();
  };

  const uploadFile = async () => {
    if (!file) {
      alert("请先选择 PDF 文件");
      return;
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
        let errMsg = "上传失败，请检查后端是否已启动";
        try {
          const err = await response.json();
          if (typeof err.detail === "string") errMsg = err.detail;
          else if (Array.isArray(err.detail)) errMsg = err.detail.map((d) => d.msg).join("; ");
        } catch {
          /* ignore */
        }
        alert(errMsg);
        return;
      }

      const data = await response.json();
      await fetchCollections();
      if (data.collection) {
        setCurrentCollection(data.collection);
      }
      alert(`${data.message}，共切分为 ${data.chunk_count} 个文本块`);
    } catch {
      alert("上传失败：网络错误或后端未响应，请确认 start-cloudflare.bat 正在运行");
    } finally {
      setUploading(false);
    }
  };

  const clearChat = async () => {
    if (!window.confirm("确定清空当前对话？")) return;
    await apiFetch(
      `/history?collection=${encodeURIComponent(currentCollection)}`,
      { method: "DELETE" }
    );
    setMessages([]);
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      const response = await apiFetch("/chat", {
        method: "POST",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          message: currentInput,
          collection: currentCollection || null,
        }),
      });

      if (!response.ok) {
        let errMsg = "发送失败，请检查后端与 API Key 配置";
        try {
          const err = await response.json();
          if (err.detail) errMsg = err.detail;
        } catch {
          /* ignore */
        }
        alert(errMsg);
        setMessages((prev) => prev.slice(0, -1));
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiText = "";

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        aiText += decoder.decode(value);
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            role: "assistant",
            content: aiText,
          };
          return newMessages;
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const currentMeta = collections.find((c) => c.name === currentCollection);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* 左侧知识库 */}
      <div
        style={{
          width: "250px",
          background: "#202123",
          color: "white",
          padding: "20px",
          flexShrink: 0,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h3 style={{ margin: 0 }}>知识库</h3>
        {username && (
          <p style={{ fontSize: "13px", color: "#8e8ea0", margin: "8px 0 0" }}>
            {username}
          </p>
        )}
        <button
          onClick={() => {
            clearToken();
            onLogout?.();
          }}
          style={{
            marginTop: "12px",
            padding: "6px 10px",
            border: "1px solid #555",
            borderRadius: "6px",
            background: "transparent",
            color: "#ccc",
            cursor: "pointer",
            fontSize: "13px",
          }}
        >
          退出登录
        </button>
        <div
          onClick={() => selectCollection("")}
          style={{
            padding: "10px",
            marginTop: "10px",
            borderRadius: "8px",
            cursor: "pointer",
            background: currentCollection === "" ? "#444654" : "transparent",
            fontSize: "14px",
          }}
        >
          普通聊天
        </div>
        {collections.length === 0 && (
          <p style={{ color: "#8e8ea0", fontSize: "14px", marginTop: "16px" }}>
            暂无知识库，请先上传 PDF
          </p>
        )}
        {collections.map((item) => (
          <div
            key={item.name}
            onClick={() => selectCollection(item.name)}
            style={{
              padding: "10px",
              marginTop: "10px",
              borderRadius: "8px",
              cursor: "pointer",
              background:
                currentCollection === item.name ? "#444654" : "transparent",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 500 }}>{item.name}</div>
              <div style={{ fontSize: "12px", color: "#8e8ea0", marginTop: "4px" }}>
                {item.chunk_count} 个文本块
              </div>
            </div>
            <button
              onClick={(e) => deleteCollection(item.name, e)}
              title="删除知识库"
              style={{
                border: "none",
                background: "transparent",
                color: "#8e8ea0",
                cursor: "pointer",
                fontSize: "16px",
                padding: "0 4px",
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* 右侧聊天区 */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          background: "#f5f5f5",
          minWidth: 0,
        }}
      >
        <div
          style={{
            padding: "10px 20px",
            background: currentCollection ? "#e6f4ff" : "#fafafa",
            borderBottom: "1px solid #ddd",
            fontSize: "14px",
            color: currentCollection ? "#0958d9" : "#666",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>
            {currentCollection
              ? `当前知识库：${currentCollection}${
                  currentMeta ? `（${currentMeta.chunk_count} 个文本块）` : ""
                }`
              : "普通聊天模式（不检索文档）"}
          </span>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              style={{
                border: "1px solid #ddd",
                background: "white",
                borderRadius: "6px",
                padding: "4px 10px",
                cursor: "pointer",
                fontSize: "13px",
              }}
            >
              清空对话
            </button>
          )}
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "20px" }}>
          {messages.length === 0 && (
            <p style={{ color: "#999", textAlign: "center", marginTop: "40px" }}>
              {currentCollection
                ? `已选择「${currentCollection}」，提问将只检索该知识库`
                : collections.length > 0
                  ? "可选择左侧知识库进行文档问答，或保持「普通聊天」"
                  : "上传 PDF 创建知识库，或直接普通聊天"}
            </p>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  maxWidth: "70%",
                  padding: "12px",
                  borderRadius: "12px",
                  background: msg.role === "user" ? "#1677ff" : "white",
                  color: msg.role === "user" ? "white" : "black",
                  lineHeight: "1.6",
                }}
              >
                <ReactMarkdown
                  components={{
                    code({ inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || "");
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={tomorrow}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, "")}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          {loading && (
            <p style={{ color: "#999", fontSize: "14px" }}>AI 正在思考...</p>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div
          style={{
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            background: "white",
            borderTop: "1px solid #ddd",
          }}
        >
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
          <div style={{ display: "flex" }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage()}
              disabled={loading}
              placeholder={
                currentCollection
                  ? `向「${currentCollection}」提问...`
                  : "普通聊天，请输入内容..."
              }
              style={{
                flex: 1,
                height: "50px",
                padding: "0 15px",
                borderRadius: "10px",
                border: "1px solid #ddd",
                fontSize: "16px",
                outline: "none",
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading}
              style={{
                marginLeft: "10px",
                width: "100px",
                border: "none",
                borderRadius: "10px",
                background: loading ? "#91caff" : "#1677ff",
                color: "white",
                fontSize: "16px",
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "发送中" : "发送"}
            </button>
            <button
              onClick={uploadFile}
              disabled={uploading}
              style={{
                marginLeft: "10px",
                width: "100px",
                border: "none",
                borderRadius: "10px",
                background: uploading ? "#95de64" : "#52c41a",
                color: "white",
                fontSize: "16px",
                cursor: uploading ? "not-allowed" : "pointer",
              }}
            >
              {uploading ? "上传中" : "上传PDF"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
