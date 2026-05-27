# 最简单上线方式（3 步）

**一个地址 = 网页 + 后端**，不用 Blueprint、不用 GitHub Pages、不用隧道。

---

## 第 1 步：打开 Render，新建 Web Service

1. 打开 https://dashboard.render.com
2. 点 **New +** → **Web Service**（不是 Blueprint）
3. 选 GitHub 仓库 **`lyon1n/ai-chat-project`**

---

## 第 2 步：填 4 个选项

| 选项 | 填什么 |
|------|--------|
| **Language** | 选 **Docker** |
| **Name** | `ai-chat`（随意） |
| **Plan** | Free |

环境变量只填 2 个：

| Key | Value |
|-----|-------|
| `DEEPSEEK_API_KEY` | 你 `.env` 里的密钥 |
| `JWT_SECRET_KEY` | 随便一串，如 `my-secret-2026` |

其余不用填（代码里已默认 SQLite）。

---

## 第 3 步：Create Web Service，等 10 分钟

部署完成后 Render 给你一个地址，例如：

```
https://ai-chat-xxxx.onrender.com
```

**打开这个地址就是完整网站**：登录、上传 PDF、聊天，全在一个链接里。

---

## 本地开发（不变）

```powershell
# 终端 1
uvicorn main:app --reload

# 终端 2
cd frontend && npm run dev
```

---

## 常见问题

**Q：免费版数据会丢吗？**  
A：重启后上传的 PDF 可能清空，但功能正常。学习/demo 够用。

**Q：为什么不用 Blueprint？**  
A：免费版不支持磁盘，Blueprint 容易失败。Docker 方式更简单。

**Q：还要 GitHub Pages 吗？**  
A：不用了，Render 一个地址搞定全部。
