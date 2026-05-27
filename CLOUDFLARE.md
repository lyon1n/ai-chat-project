# Cloudflare 隧道公网访问（无需银行卡）

**一个链接 = 完整网站**，电脑开着时任何人都能访问。

---

## 第一次使用（只需一次）

```powershell
cd c:\Users\acer\Desktop\ai-chat-project
.\scripts\build-static.ps1
```

---

## 每次要公网访问时

```powershell
cd c:\Users\acer\Desktop\ai-chat-project
.\scripts\start-cloudflare.ps1
```

终端里会出现类似：

```
https://random-words-here.trycloudflare.com
```

**复制这个地址**，浏览器打开 = 完整 AI 知识库网站（登录、上传 PDF、聊天）。

---

## 说明

| 项目 | 说明 |
|------|------|
| 要不要绑卡 | **不要**，Cloudflare 快速隧道免费 |
| 电脑要开着吗 | **要**，关电脑或关脚本后链接失效 |
| 地址会变吗 | **每次重启脚本可能变**，以终端里显示的为准 |
| 和 Render 比 | 不用绑卡，但需要你电脑在线 |

---

## 本地自用（不启隧道）

```powershell
uvicorn main:app --reload
cd frontend && npm run dev
```

打开 http://localhost:5173

---

## 常见问题

**Q：提示找不到 cloudflared？**
```powershell
winget install Cloudflare.cloudflared
```
关闭终端重新打开，再运行 `start-cloudflare.ps1`。

**Q：打开链接很慢？**  
第一次请求会加载模型，等几秒即可。

**Q：想要固定不变的域名？**  
需要有自己的域名并接入 Cloudflare（免费账号即可），那是进阶步骤，需要再说。
