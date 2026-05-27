import { useState } from "react";
import { API, setToken } from "./api";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    if (!username.trim() || !password) {
      setError("请输入用户名和密码");
      return;
    }

    setLoading(true);
    setError("");

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
        setMode("login");
        setError("");
        alert("注册成功，请登录");
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
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f0f2f5",
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
        <h2 style={{ margin: "0 0 8px", textAlign: "center" }}>
          AI 知识库聊天
        </h2>
        <p style={{ margin: "0 0 24px", textAlign: "center", color: "#888" }}>
          {mode === "login" ? "登录你的账号" : "创建新账号"}
        </p>

        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="用户名"
          style={inputStyle}
        />
        <input
          type="password"
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

        <button
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

        <p style={{ textAlign: "center", marginTop: "16px", fontSize: "14px" }}>
          {mode === "login" ? (
            <>
              没有账号？{" "}
              <span
                onClick={() => setMode("register")}
                style={{ color: "#1677ff", cursor: "pointer" }}
              >
                去注册
              </span>
            </>
          ) : (
            <>
              已有账号？{" "}
              <span
                onClick={() => setMode("login")}
                style={{ color: "#1677ff", cursor: "pointer" }}
              >
                去登录
              </span>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

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
