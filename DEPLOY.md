# 部署清单（按顺序打勾）

## ✅ 已完成

- [x] 代码已推送到 GitHub：https://github.com/lyon1n/ai-chat-project

## 第二步：部署后端（Render）— 约 5 分钟

1. 打开：**https://dashboard.render.com/**
2. 登录后 → **New +** → **Blueprint**
3. 连接 GitHub 仓库 `lyon1n/ai-chat-project`
4. Render 会读取 `render.yaml`，点击 **Apply**
5. 在环境变量界面填写（必填）：

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | 你的 DeepSeek 密钥 |
| `JWT_SECRET_KEY` | 任意随机长字符串 |
| `DATABASE_URL` | 云端 MySQL 连接串（见第三步） |
| `MYSQL_SSL` | `true` |
| `ALLOWED_ORIGINS` | 先填 `https://lyon1n.github.io`，部署前端后再改成 Pages 完整地址 |

6. 等待部署完成，记下地址，例如：`https://ai-chat-api.onrender.com`
7. 访问 `https://你的地址.onrender.com/health` 应返回 `{"status":"ok"}`

## 第三步：云端 MySQL（任选其一）

**方案 A — Railway（推荐，有免费额度）**

1. https://railway.app → New Project → **MySQL**
2. 复制 `MYSQL_URL` 或连接信息，格式化为：
   `mysql://user:pass@host:3306/railway`
3. 填入 Render 的 `DATABASE_URL`

**方案 B — 其他 MySQL 云服务商**

- Aiven、TiDB Cloud、自建 VPS MySQL 均可
- 连接串填入 `DATABASE_URL`，SSL 开启时设 `MYSQL_SSL=true`

## 第四步：启用 GitHub Pages 前端

1. 打开：https://github.com/lyon1n/ai-chat-project/settings/secrets/actions
2. **New repository secret**：
   - Name: `VITE_API_URL`
   - Value: `https://你的Render地址.onrender.com`（不要末尾斜杠）
3. 打开：https://github.com/lyon1n/ai-chat-project/settings/pages
   - Source 选 **GitHub Actions**
4. 推送代码或手动运行 Actions：**Actions** → **Deploy Frontend** → **Run workflow**
5. 部署完成后前端地址：`https://lyon1n.github.io/ai-chat-project/`

## 第五步：回改 CORS

Render 环境变量 `ALLOWED_ORIGINS` 改为：

```
https://lyon1n.github.io,https://lyon1n.github.io/ai-chat-project
```

## 验证

- [ ] 打开 GitHub Pages 链接，能看到登录页
- [ ] 注册 / 登录成功
- [ ] 上传 PDF、聊天正常

## 可选：Vercel 替代 GitHub Pages

1. https://vercel.com → Import `lyon1n/ai-chat-project`
2. Root Directory: `frontend`
3. 环境变量 `VITE_API_URL` = Render 后端地址
4. 更新 Render 的 `ALLOWED_ORIGINS` 为 Vercel 域名
