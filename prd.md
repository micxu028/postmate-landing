# PostMate — 产品需求手册 (PRD)

> 版本: v1.0 | 更新: 2026-05-21 | 状态: Draft

---

## 1. 产品概述

### 1.1 一句话
每周自动生成 Instagram/Facebook 内容的 AI 工具，美国小商家不用动手，$29/月。

### 1.2 核心价值
从「排期工具」变成「AI 社媒运营外包」。用户花 3 分钟注册，之后不用管。

### 1.3 首批行业
瑜伽馆 / 健身工作室 / 普拉提馆（内容套路固定、视觉需求明确、愿意付费）

### 1.4 目标用户
- 美国本地小商家（< 10 人）
- 老板就是运营者，没时间做社媒
- Instagram/Facebook 更新不规律
- 愿意为省时间付 $29/月

---

## 2. MVP 范围 (V1)

### 2.1 功能清单

| 功能 | 优先级 | 说明 |
|------|--------|------|
| Landing Page | P0 | ✅ 已完成 |
| 用户注册 | P0 | 邮箱 + 密码注册 |
| Brand Onboarding | P0 | 填品牌信息、选风格、上传图片 |
| AI 内容生成 | P0 | DeepSeek 生成 caption + hashtags |
| AI 图片生成 | P0 | 通过 MJ 代理生成配图 |
| 内容预览 | P0 | 看下周 7 条帖子 |
| 邮件通知 | P1 | 内容就绪时通知用户 |
| Beta 邀请流程 | P1 | 通过邮件邀请，限免使用 |

### 2.2 V1 不做

| 不做 | 原因 |
|------|------|
| Instagram/Facebook OAuth 发布 | MVP 只预览，不发布 |
| 定时自动发布 | 同上 |
| Stripe/PayPal 支付 | MVP 免费，付费下一版 |
| 数据分析 | MVP 不需要 |
| TikTok | 视频 AI 质量不够 |
| 多语言 | 只做英文 |
| 团队协作 | 用户都是个体户 |
| 移动 App | 网页够用 |

---

## 3. 用户流程

```
Landing Page → 注册 → Onboarding → AI 生成 → 预览 Dashboard
                                               ↓
                                （循环）等待下周内容 ← 满意？→ 是，等通知
                                                      → 否，重新生成
```

### 3.1 注册流程
1. 用户在 Landing Page 输入邮箱
2. 收到确认邮件 → 设密码 → 登录
3. 进入 Onboarding

### 3.2 Onboarding 流程
1. 填工作室名称、地址、电话
2. 选行业（瑜伽/健身/普拉提）
3. 选风格：专业/温暖/活泼/极简
4. 上传 5-10 张品牌图片（作为 AI 图片生成的风格参考）
5. 选发布频率：每周 3/5/7 条
6. 确定 → 进入生成

### 3.3 内容生成流程
1. 用户完成 Onboarding → 触发首次生成
2. 后端调 DeepSeek 生成 7 条 caption + hashtag 组合
3. 后端调 MJ 代理生成 7 张配图
4. 内容存入数据库 → 推送到前端
5. 用户看到预览 Dashboard

### 3.4 预览 Dashboard
- 显示 7 张卡片（周一到周日）
- 每张展示：[图片] + caption + hashtags
- 操作：批准 / 重新生成单条 / 全部重新生成
- 每周自动生成下一周内容

---

## 4. 技术架构

### 4.1 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | HTML + CSS + Vanilla JS | 先做简单版，不改框架 |
| 后端 | Python FastAPI | 异步，性能够 |
| 数据库 | Supabase (PostgreSQL) | 免费版，500MB |
| AI 文本 | DeepSeek API | 国内直连，¥2/百万 token |
| AI 图片 | 国内 MJ 代理 | ¥0.2-0.5/张 |
| 部署 | Railway | 美西服务器 |
| 发送邮件 | Brevo | 免费版 300封/天 |
| 域名 | postmate.net | Cloudflare DNS + Pages |

### 4.2 数据库设计

#### users 表
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);
```

#### brands 表
```sql
CREATE TABLE brands (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) NOT NULL,
  name TEXT NOT NULL,
  industry TEXT NOT NULL,         -- yoga / fitness / pilates
  style TEXT NOT NULL,            -- professional / warm / energetic / minimalist
  tone TEXT NOT NULL,             -- professional / friendly / humorous / inspirational
  post_frequency INT DEFAULT 7,  -- posts per week: 3, 5, or 7
  city TEXT,
  state TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### brand_images 表
```sql
CREATE TABLE brand_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID REFERENCES brands(id) NOT NULL,
  url TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### posts 表
```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID REFERENCES brands(id) NOT NULL,
  week_start DATE NOT NULL,       -- 所属周
  day_of_week INT NOT NULL,       -- 0=周一 ... 6=周日
  caption TEXT NOT NULL,
  hashtags TEXT[] NOT NULL,
  image_url TEXT,
  status TEXT DEFAULT 'pending',  -- pending / approved / rejected / regenerating
  created_at TIMESTAMPTZ DEFAULT NOW(),
  approved_at TIMESTAMPTZ
);
```

#### generation_logs 表
```sql
CREATE TABLE generation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID REFERENCES brands(id) NOT NULL,
  type TEXT NOT NULL,             -- text / image
  status TEXT NOT NULL,           -- success / failed
  prompt TEXT,
  response TEXT,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.3 API 接口设计

```
POST   /api/auth/register        — 注册
POST   /api/auth/login           — 登录
GET    /api/auth/me              — 当前用户信息

POST   /api/brands               — 创建品牌资料
GET    /api/brands/me            — 获取我的品牌
PUT    /api/brands/me            — 更新品牌资料
POST   /api/brands/images        — 上传品牌图片

POST   /api/generate             — 触发内容生成
GET    /api/posts?week=2026-05-25 — 获取某周内容
PUT    /api/posts/:id/approve    — 批准单条内容
PUT    /api/posts/:id/regenerate — 重新生成单条
PUT    /api/posts/regenerate-all — 全部重新生成

GET    /api/invite/:code         — Beta 邀请验证
```

---

## 5. AI Prompt 设计

### 5.1 Caption 生成 Prompt

```
You are a social media manager for a [industry] studio called [brand_name] located in [city], [state].
Brand style: [style]
Brand tone: [tone]

Generate [frequency] Instagram captions for next week (one per day).
Each caption should be:
- 100-200 characters
- Include relevant emojis
- End with a call-to-action
- In American English, natural and not salesy

For each caption, also provide:
- 8-12 relevant hashtags
- An image description / prompt that matches the caption (for AI image generation)

Output format: JSON array of {day, caption, hashtags, image_prompt}
```

### 5.2 Image Prompt 生成逻辑

基于 caption 内容 + 品牌风格，生成 MJ 可用的 prompt：

```
Subject: [based on caption]
Style: [brand style], clean composition
Mood: [matching the caption tone]
Colors: brand-aligned palette
--ar 1:1 --v 6
```

---

## 6. 内容格式

### 每条帖子包含
- **图片**: 1:1 方形，MJ 生成
- **Caption**: 100-200 字，包含 emoji，号召行动
- **Hashtags**: 8-12 个，混合热门 + 小众标签

### 示例
```
🧘‍♀️ Monday morning flow starts here.

Roll out your mat and set your intention for the week.
Whether it's 15 minutes or an hour — just show up.

👇 Comment "IN" for a free week of classes!
#yogaeverydamnday #austintexas #yogateacher #morningflow
#yogapractice #yogainspiration #namaste #yogajourney
#wellnessjourney #mindbodyspirit #austin #yogacommunity
```

---

## 7. 非功能性需求

| 指标 | 要求 |
|------|------|
| 页面加载 | < 3s |
| AI 生成响应 | < 30s（异步 + 轮询） |
| 可用性 | 99%（全程托管 Railway） |
| 安全 | 密码 bcrypt 加密，API 用 JWT |
| 邮件送达 | 通过 Brevo 发送 |
| 移动端 | 响应式（基于已有样式） |

---

## 8. 后续版本规划

| 版本 | 功能 | 时间 |
|------|------|------|
| V1.0 | 注册 + Onboarding + AI 生成 + 预览 | 第 1 周 |
| V1.1 | IG/FB OAuth + 自动发布 | 第 3 周 |
| V1.2 | PayPal 支付 + 付费墙 | 第 4 周 |
| V1.3 | 定时任务（每周自动生成下一周）| 第 5 周 |
| V2.0 | 简易数据分析 | TBD |
