import { useCallback, useRef, useState } from "react";
import { apiFetch, authHeaders, errorMessage } from "./api";

function replaceLastAssistant(messages, content) {
  const next = [...messages];
  next[next.length - 1] = { role: "assistant", content };
  return next;
}

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const abortRef = useRef(null);

  const fetchHistory = useCallback(async (collection) => {
    try {
      const res = await apiFetch(`/history?collection=${encodeURIComponent(collection)}`);
      if (!res.ok) throw new Error(await errorMessage(res, "获取历史失败"));
      const data = await res.json();
      setMessages(Array.isArray(data) ? data : []);
      setError("");
    } catch (err) {
      setMessages([]);
      setError(err.message || "获取历史失败");
    }
  }, []);

  const sendMessage = useCallback(async (input, collection) => {
    const trimmed = input.trim();
    if (!trimmed || loading) return false;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: trimmed },
      { role: "assistant", content: "" },
    ]);
    setLoading(true);
    setError("");

    let rafId = 0;
    let aiText = "";

    const flush = () => {
      rafId = 0;
      setMessages((prev) => replaceLastAssistant(prev, aiText));
    };

    try {
      const response = await apiFetch("/chat", {
        method: "POST",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          message: trimmed,
          collection: collection || null,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(await errorMessage(response, "发送失败，请检查后端与 API Key 配置"));
      }
      if (!response.body) {
        throw new Error("浏览器不支持流式响应");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        aiText += decoder.decode(value, { stream: true });
        if (!rafId) rafId = window.requestAnimationFrame(flush);
      }

      aiText += decoder.decode();
      if (rafId) window.cancelAnimationFrame(rafId);
      flush();
      return true;
    } catch (err) {
      if (err.name === "AbortError") {
        setError("已停止生成");
      } else {
        setError(err.message || "发送失败");
        setMessages((prev) => prev.slice(0, -2));
      }
      return false;
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  }, [loading]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return {
    messages,
    setMessages,
    loading,
    error,
    setError,
    fetchHistory,
    sendMessage,
    cancel,
  };
}
