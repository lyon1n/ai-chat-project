import { lazy, Suspense, useEffect, useMemo, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { tomorrow } from "react-syntax-highlighter/dist/esm/styles/prism";

const SyntaxHighlighter = lazy(() =>
  import("react-syntax-highlighter").then((module) => ({
    default: module.Prism,
  }))
);

export default function MessageList({ messages, loading, currentCollection, hasCollections }) {
  const listRef = useRef(null);
  const codeComponents = useMemo(
    () => ({
      code({ inline, className, children, ...props }) {
        const match = /language-(\w+)/.exec(className || "");
        return !inline && match ? (
          <Suspense fallback={<pre className="code-fallback">{children}</pre>}>
            <SyntaxHighlighter
              style={tomorrow}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          </Suspense>
        ) : (
          <code className={className} {...props}>
            {children}
          </code>
        );
      },
    }),
    []
  );

  useEffect(() => {
    listRef.current?.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: loading ? "auto" : "smooth",
    });
  }, [messages, loading]);

  return (
    <div className="message-list" ref={listRef}>
      {messages.length === 0 && (
        <p className="empty-state">
          {currentCollection
            ? `已选择「${currentCollection}」，提问将只检索该知识库`
            : hasCollections
              ? "可选择左侧知识库进行文档问答，或保持「普通聊天」"
              : "上传 PDF 创建知识库，或直接普通聊天"}
        </p>
      )}

      {messages.map((msg, index) => (
        <div className={`message-row ${msg.role}`} key={`${msg.role}-${index}`}>
          <div className="message-bubble">
            <ReactMarkdown components={codeComponents}>{msg.content}</ReactMarkdown>
          </div>
        </div>
      ))}

      {loading && <p className="thinking">AI 正在思考...</p>}
    </div>
  );
}
