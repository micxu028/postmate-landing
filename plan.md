# PostMate — 项目计划书

> 版本: v1.0 | 更新: 2026-05-21 | 状态: Draft

---

## 1. Phase 概览

| Phase | 内容 | 预计时间 | 交付物 |
|-------|------|---------|--------|
| Phase 0 | 基础设施 | 2 天 | 后端骨架 + 数据库 + 部署流水线 |
| Phase 1 | 用户系统 | 2 天 | 注册/登录 + Onboarding 流程 |
| Phase 2 | AI 内容生成 | 3 天 | DeepSeek + MJ 代理接入，内容生成 pipeline |
| Phase 3 | 预览 Dashboard | 2 天 | 前端展示 + 审批操作 |
| Phase 4 | 邮件 + Beta 流程 | 1 天 | 邀请邮件 + 通知 |
| Phase 5 | 测试 + 发信 | 2 天 | 全流程跑通，开始发邮件 |

**总计：约 12 天（含周末 2 周）**

---

## 2. Phase 0 — 基础设施（2 天）

### 目标
FastAPI 项目骨架、Supabase 数据库、Railway 部署

### 任务

| 天 | 任务 | 产出 |
|----|------|------|
| 1 | 创建 FastAPI 项目结构（main.py, config, routers, models, services） | 项目骨架 |
| 1 | Supabase 建表（SQL 迁移脚本） | 5 张表 |
| 1 | 配置 Railway 部署（GitHub 自动部署） | 部署流水线 |
| 2 | 配置 JWT 认证中间件 | auth middleware |
| 2 | 配置 CORS / 环境变量 / 日志 | 基础配置 |
| 2 | 部署 Hello World 到 Railway 验证 | 可访问 API |

### 技术决策
- FastAPI + Uvicorn（异步）
- SQLAlchemy async + asyncpg 连 Supabase
- PyJWT + bcrypt 做认证
- Railway 绑定 GitHub 仓库，push 自动部署
- 环境变量管理：.env → Railway 环境变量面板

---

## 3. Phase 1 — 用户系统（2 天）

### 目标
用户注册、登录、Brand Onboarding 完整流程

### 任务

| 天 | 任务 | 产出 |
|----|------|------|
| 1 | `POST /api/auth/register` — 注册接口 | 注册 API |
| 1 | `POST /api/auth/login` — 登录接口，返回 JWT | 登录 API |
| 1 | 注册确认邮件（Brevo SMTP） | 邮件模板 |
| 2 | `POST /api/brands` — 创建品牌资料 | Onboarding API |
| 2 | `POST /api/brands/images` — 上传品牌图片（Base64 或 URL） | 图片上传 |
| 2 | Onboarding 前端页面（多步骤表单） | 前端页面 |

### Onboarding 页面设计
4 步表单，每步一页：
1. **工作室信息**: 名称、城市、州、电话
2. **行业 + 风格**: 行业选择（瑜伽/健身/普拉提） + 风格选择（专业/温暖/活泼/极简）
3. **上传图片**: 5-10 张品牌图片（展示风格）
4. **偏好设置**: 每周发几条（3/5/7）+ 确认

---

## 4. Phase 2 — AI 内容生成（3 天）

### 目标
接入 DeepSeek API + MJ 代理，实现完整的内容生成 pipeline

### 任务

| 天 | 任务 | 产出 |
|----|------|------|
| 1 | DeepSeek API 接入（SDK 封装 + prompt 模板） | text gen service |
| 1 | 调优 Caption 生成 prompt（行业差异化） | 行业模板 |
| 1 | 测试生成输出格式 | 稳定输出 |
| 2 | MJ 代理 API 接入（图片生成） | image gen service |
| 2 | 基于 caption 生成 image prompt | prompt builder |
| 2 | 异步生成 pipeline（先文本后图片） | pipeline |
| 3 | `POST /api/generate` — 生成接口 | 生成 API |
| 3 | 生成进度轮询（前端展示生成状态） | 进度反馈 |
| 3 | 容错 + 重试机制（AI 调用可能失败） | 稳定性 |

### AI 调用架构
```
用户触发 → API 收到请求 → 返回 202 Accepted（异步）
  → 后台任务启动
    → Step 1: DeepSeek 生成 7 条 caption + hashtags + image_prompt
    → Step 2: 并行调 MJ 代理生成 7 张图片
    → Step 3: 存入 posts 表
  → 前端轮询 /api/posts 直到全部就绪
```

### 失败处理
- DeepSeek 失败 → 重试 2 次 → 换 simpler prompt → 报错
- MJ 失败 → 单独重试该图片 → 用备用 prompt → 跳过（标记无图）
- 部分成功 → 能展示多少展示多少

---

## 5. Phase 3 — 预览 Dashboard（2 天）

### 目标
用户看到生成的 7 条帖子，能操作审批

### 任务

| 天 | 任务 | 产出 |
|----|------|------|
| 1 | Dashboard 页面布局（7 张卡片，日历视图） | 页面框架 |
| 1 | 单条帖子展示（图片 + caption + hashtags） | 卡片组件 |
| 1 | 加载状态 / 空状态 / 错误状态 | 完整状态 |
| 2 | 批准按钮 → `PUT /api/posts/:id/approve` | 单条批准 |
| 2 | 重新生成按钮 → `PUT /api/posts/:id/regenerate` | 单条重生成 |
| 2 | 全部重新生成按钮 | 批量重生成 |
| 2 | 周切换（上周/下周） | 周导航 |

### Dashboard 状态说明
- **加载中**: 骨架屏（每张卡片灰色脉冲动画）
- **生成中**: 卡片显示进度，每完成一张出现一张
- **完成**: 全部展示，底部显示「下周内容已就绪」
- **拒绝**: 单条显示「已标记重新生成」，后台异步替换
- **空状态**: 还没有内容，显示「点击生成下周内容」按钮

---

## 6. Phase 4 — 邮件 + Beta 流程（1 天）

### 目标
邮件通知 + Beta 邀请管理

### 任务

| 天 | 任务 | 产出 |
|----|------|------|
| 1 | 内容就绪邮件通知模板 | 通知邮件 |
| 1 | Beta 邀请码生成 + 验证接口 | 邀请系统 |
| 1 | 注册 Brevo + 域名验证 DNS | 邮件基础设施 |
| 1 | 发信脚本（从 leads.csv 读取 + SMTP 发送） | cold email script |

### Beta 邀请流程
```
管理员（你） → 用脚本发邮件给 leads → 对方回复/点击链接
  → 获得 Beta 邀请码 → 去 postmate.net/signup?code=xxx 注册
  → 走正常 Onboarding 流程
  → 免费使用（没有支付环节）
```

---

## 7. Phase 5 — 测试 + 发信（2 天）

### 目标
全流程走通，开始对外发邮件

### 任务

| 天 | 任务 | 产出 |
|----|------|------|
| 1 | 全流程测试（从注册到预览） | 已验收 |
| 1 | 修 bug + 打磨细节 | 稳定版 |
| 2 | 发第一批邮件（10 封，手动观察回复） | 第一轮 outreach |
| 2 | 根据回复调整邮件模板 | 优化版 |
| 2 | 继续发剩余 leads | 推广启动 |

---

## 8. 依赖关系

```
Phase 0 (基础设施)
  └── Phase 1 (用户系统)
        └── Phase 2 (AI 生成)
              └── Phase 3 (预览 Dashboard)
Phase 1 + Phase 4 (邮件) → Phase 5 (发信)
```

Phase 4 可以和 1/2/3 并行进行。

---

## 9. 风险

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| DeepSeek API 不稳定 | 低 | 生成失败 | 备选 prompt + 重试机制 |
| MJ 代理出图慢 | 中 | 等待时间长 | 异步生成，前端显示进度 |
| Railway 国内访问慢 | 中 | 开发调试不便 | 操作时走代理 |
| Brevo 域名验证失败 | 低 | 无法发邮件 | 换方案（SendGrid / Zoho）|
| beta 用户不回复 | 中 | 没有验证反馈 | 多发 50 封 + 优化文案 |
| 代理不稳定影响开发 | 中 | 无法 push/部署 | 准备备用节点（已配 5 个）|

---

## 10. Phase 0 启动条件

✅ Namecheap 域名已买（postmate.net）
✅ Cloudflare DNS 已配
✅ Landing Page 已部署
✅ 代理（mihomo + Just My Socks）运行中
✅ 开发环境就绪

✅ Brevo 已注册（换了邮箱）
❌ 需要先做：注册 Supabase（免费版）
❌ 需要先做：注册 Railway（免费版，绑 GitHub）

---

## 11. 第一阶段具体行动

### 当前待办
1. ~~注册 Supabase — 我来操作~~ ✅ 已完成
2. 注册 Railway — 需要 GitHub 账号
3. DeepSeek API Key 填进 .env
