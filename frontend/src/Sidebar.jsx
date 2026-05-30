import { clearToken } from "./api";

export default function Sidebar({
  collections,
  currentCollection,
  onSelectCollection,
  onDeleteCollection,
  onLogout,
}) {
  return (
    <aside className="sidebar">
      <h3>知识库</h3>
      <button
        className="ghost-button"
        type="button"
        onClick={() => {
          clearToken();
          onLogout?.();
        }}
      >
        退出登录
      </button>

      <button
        className={`collection-item ${currentCollection === "" ? "active" : ""}`}
        type="button"
        onClick={() => onSelectCollection("")}
      >
        普通聊天
      </button>

      {collections.length === 0 && (
        <p className="sidebar-empty">暂无知识库，请先上传 PDF</p>
      )}

      {collections.map((item) => (
        <button
          className={`collection-item with-action ${
            currentCollection === item.name ? "active" : ""
          }`}
          key={item.name}
          type="button"
          onClick={() => onSelectCollection(item.name)}
        >
          <span className="collection-meta">
            <strong>{item.name}</strong>
            <small>{item.chunk_count} 个文本块</small>
          </span>
          <span
            className="delete-collection"
            role="button"
            tabIndex={0}
            title="删除知识库"
            onClick={(event) => {
              event.stopPropagation();
              onDeleteCollection(item.name);
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                event.stopPropagation();
                onDeleteCollection(item.name);
              }
            }}
          >
            ×
          </span>
        </button>
      ))}
    </aside>
  );
}
