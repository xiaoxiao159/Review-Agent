# Review Agent

一个面向商品评论分析的全栈项目（FastAPI + Celery + LangGraph + Chroma + Vue），用于异步生成结构化“差评分析报告”。

---

## 1. 这个版本是干什么的？

**版本定位：全栈登录版 MVP（Auth Center + 报告分析）**。

这个版本已经从“手动粘贴 token 调试”升级为“用户登录后使用系统”的模式，适合演示与内部试运行：

- 用户注册/登录后获得访问能力
- 前端提交分析任务
- 后端异步生成报告（Celery）
- 前端自动轮询状态并展示结果图表

核心价值：把分散评论快速转成结构化洞察，并具备基本账号体系。

---

## 2. 解决了什么问题？

### 业务痛点

1. 评论量大，人工低效
2. 负面反馈不成体系，定位慢
3. 历史相似差评难复用
4. 原先“手填 token”不符合真实产品体验

### 本版本解决方案

- 自动识别负向评论（评分/情感规则）
- 自动分类原因、提取关键词、生成建议
- Chroma 检索同商品历史相似差评（Top-5）
- 前端可视化展示趋势与案例
- 引入 Auth Center：注册、登录、刷新、登出、当前用户信息

---

## 3. 功能清单

### 3.1 认证中心 API

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/forgot-password`（占位通用响应）

### 3.2 报告 API（需登录）

- `POST /api/v1/reports/analyze`：提交任务，返回 `task_id`
- `GET /api/v1/reports/status/{task_id}`：查询状态
- `GET /api/v1/reports/{task_id}`：获取完整报告

### 3.3 前端（Vue）

- 登录/注册切换
- 登录后提交分析与轮询
- 报告详情展示
- 趋势图可视化（ECharts）

---

## 4. 技术架构

### 后端

- FastAPI（接口）
- SQLAlchemy + asyncpg（PostgreSQL）
- Celery + Redis（异步任务）
- LangGraph（流程编排）
- Chroma（向量检索）
- JWT + refresh session（认证中心）

### 前端

- Vue 3 + TypeScript + Vite
- Axios（带自动注入 access token + 401 刷新）
- ECharts + vue-echarts

### 部署

- Docker Compose
- 服务：`api` / `worker` / `frontend` / `postgres` / `redis`

---

## 5. 快速启动（可直接打开页面）

### 5.1 准备配置

在项目根目录 `review-agent`：

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

> Windows PowerShell 可用：
>
> `copy .env.example .env`
>
> `copy frontend\.env.example frontend\.env`

### 5.2 启动全栈

```bash
docker compose up -d --build
```

### 5.3 直接访问

- 后端文档（Swagger）：`http://localhost:8000/docs`
- 前端页面：`http://localhost:5173`
- 健康检查：`http://localhost:8000/health`

---

## 6. 登录与使用

### 6.1 默认管理员（启动自动初始化）

默认来自 `.env`：

- username: `admin`
- password: `Admin@123456`

可在 `.env` 中改：

- `DEFAULT_ADMIN_USERNAME`
- `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_ADMIN_EMAIL`

### 6.2 前端使用流程

1. 打开 `http://localhost:5173`
2. 用管理员账号登录
3. 输入 `product_id`（可选日期范围）
4. 点击“开始分析”
5. 等待状态变为 `completed`，查看报告

---

## 7. 关键环境变量（认证相关）

```env
JWT_SECRET=
JWT_REFRESH_SECRET=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=7
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=Admin@123456
DEFAULT_ADMIN_ENABLED=true
```

---

## 8. 测试与验证

> 说明：首次冷启动会拉很多 Python 包，网络慢时需要更久。

```bash
docker compose exec api bash -lc "pip install -r requirements.txt && python -m pytest --cov=app --cov-report=term-missing"
```

前端构建验证：

```bash
docker compose exec frontend npm run build
```

---

## 9. 常见问题

### 9.1 API 显示 unhealthy

通常是首次启动 `pip install` 还在下载依赖，服务未到 uvicorn 阶段。

查看日志：

```bash
docker compose logs -f api
```

本项目已增加 `start_period`，减少冷启动误判。

### 9.2 前端能开，docs 打不开

先确认 API 状态：

```bash
docker compose ps
```

若 `api` 仍 `starting/unhealthy`，继续看 `docker compose logs -f api`。

### 9.3 登录失败

- 检查 `.env` 中默认管理员密码是否被修改
- 检查数据库是否被重建（首次启动后管理员会写入 DB）

---

## 10. 安全注意事项

- 不要把真实密钥写进 `.env.example`
- 已泄露过的密钥必须轮换
- 生产环境建议密钥托管，不用明文文件

---

## 11. 下一步优化建议

1. 引入 Dockerfile（依赖构建期安装，缩短启动时间）
2. Alembic 管理 users/auth_sessions/reviews 迁移
3. 认证增强：邮箱验证、找回密码真流程、登录限流
4. 前端拆分页面（Login/Dashboard 路由）
5. 任务可观测性（耗时、失败原因、队列指标）

---

## 12. License

内部项目，按团队规范处理。