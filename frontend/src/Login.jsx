import { useState } from "react";
import { API, setToken } from "./api";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const switchMode = (next) => {
    setMode(next);
    setError("");
    setSuccess("");
  };

  const submit = async () => {
    if (!username.trim() || !password) {
      setError("请输入用户名和密码");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const endpoint = mode === "login" ? "/login" : "/register";
      const res = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.error || "操作失败");
        return;
      }

      if (mode === "register") {
        switchMode("login");
        setSuccess("注册成功，请登录");
        return;
      }

      setToken(data.token);
      onLogin(data);
    } catch {
      setError("网络错误，请确认后端已启动");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f0f2f5",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          width: "360px",
          padding: "32px",
          background: "white",
          borderRadius: "12px",
          boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
        }}
      >
        <h2 style={{ margin: "0 0 20px", textAlign: "center", color: "#000" }}>
          AI 知识库聊天
        </h2>

        <div
          style={{
            display: "flex",
            marginBottom: "24px",
            borderRadius: "8px",
            background: "#f5f5f5",
            padding: "4px",
          }}
        >
          <button
            type="button"
            onClick={() => switchMode("login")}
            style={tabStyle(mode === "login")}
          >
            登录
          </button>
          <button
            type="button"
            onClick={() => switchMode("register")}
            style={tabStyle(mode === "register")}
          >
            注册
          </button>
        </div>

        <p style={{ margin: "0 0 16px", textAlign: "center", color: "#666" }}>
          {mode === "login" ? "登录你的账号" : "创建新账号"}
        </p>

        <input
          aria-label="用户名"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="用户名"
          style={inputStyle}
        />
        <input
          aria-label="密码"
          type="password"
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="密码（至少 6 位）"
          style={{ ...inputStyle, marginTop: "12px" }}
        />

        {error && (
          <p style={{ color: "#ff4d4f", fontSize: "14px", marginTop: "12px" }}>
            {error}
          </p>
        )}
        {success && (
          <p style={{ color: "#16a34a", fontSize: "14px", marginTop: "12px" }}>
            {success}
          </p>
        )}

        <button
          type="button"
          onClick={submit}
          disabled={loading}
          style={{
            width: "100%",
            marginTop: "20px",
            height: "44px",
            border: "none",
            borderRadius: "8px",
            background: loading ? "#91caff" : "#1677ff",
            color: "white",
            fontSize: "16px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "请稍候..." : mode === "login" ? "登录" : "注册"}
        </button>
      </div>
    </div>
  );
}

const tabStyle = (active) => ({
  flex: 1,
  height: "36px",
  border: "none",
  borderRadius: "6px",
  background: active ? "#fff" : "transparent",
  color: active ? "#1677ff" : "#666",
  fontSize: "15px",
  fontWeight: active ? 600 : 400,
  cursor: "pointer",
  boxShadow: active ? "0 1px 4px rgba(0,0,0,0.08)" : "none",
});

const inputStyle = {
  width: "100%",
  height: "44px",
  padding: "0 12px",
  borderRadius: "8px",
  border: "1px solid #ddd",
  fontSize: "15px",
  outline: "none",
  boxSizing: "border-box",
};
