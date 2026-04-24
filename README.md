# 🚀 Review Agent — 用户评论智能分析系统

> 一个面向产品与运营团队的 AI 分析系统，将海量用户评论转化为结构化、可执行的产品改进洞察。

---

## 🧩 一、项目背景

在真实业务中，产品团队通常面临以下问题：

- 用户评论数量快速增长，人工阅读成本极高  
- 负面反馈分散，难以归类和总结  
- 相同问题反复出现，但缺乏复用机制  
- 产品决策依赖经验，而非数据支持  

👉 最终结果：

> **团队知道“有问题”，但不知道“问题在哪里、为什么发生、优先解决什么”。**

---

## 💡 二、项目解决方案

**Review Agent** 提供评论分析能力，将“原始评论”转化为“可执行决策信息”。

系统自动完成：

- 📊 负面评论结构化总结（Summary）
- 🧠 问题原因分析（Root Cause Analysis）
- 🏷️ 关键词与问题分类
- 💡 改进建议生成
- 🔁 相似历史问题检索（向量搜索）
- 📈 趋势可视化分析

---

## 🎯 三、适用人群

- 产品经理：定位核心问题，辅助决策  
- 运营团队：监控用户反馈趋势  
- 客服团队：识别高频投诉  

---

## ⭐ 四、项目亮点

### 1. 不只是情感分析，而是问题归因
不仅判断“好/坏”，还能分析：
> 用户为什么不满？

---

### 2. 检索增强分析（RAG 实战）
- 使用 Chroma 做语义检索  
- 引入历史相似案例  
- 提升分析结果的稳定性和可解释性  

---

### 3. 异步任务架构（接近真实生产）
- Celery + Redis 处理长任务  
- 前端轮询任务状态  
- 支持大规模评论分析  

---

### 4. 完整产品闭环
包含：

- 用户系统（登录/注册）
- 任务提交
- 异步处理
- 数据存储
- 可视化展示

---

## 🏗️ 五、系统架构

```

[ Vue Dashboard ]
|
| HTTP (JWT)
v
[ FastAPI API Layer ]
|
| enqueue task
v
[ Celery + Redis Queue ]
|
| async processing
v
[ LangGraph Pipeline ]
|
| retrieval
v
[ Chroma Vector Store ]
|
v
[ PostgreSQL ]

````

---

## ⚙️ 六、核心流程

1. 用户登录并提交分析请求  
2. 后端创建任务并返回 `task_id`  
3. Worker 加载评论数据  
4. 执行向量检索获取相似案例  
5. LangGraph 进行多阶段分析  
6. 结果写入数据库  
7. 前端轮询并展示分析报告  

---

## 🧱 七、技术栈

### Backend
- FastAPI  
- SQLAlchemy (async) + asyncpg  
- Celery + Redis  
- LangGraph  
- ChromaDB  
- JWT Authentication  

### Frontend
- Vue 3 + TypeScript + Vite  
- Axios（自动刷新 Token）  
- ECharts  

### Infrastructure
- Docker Compose  
- PostgreSQL + Redis  

---

## 🖥️ 八、主要功能

### 8.1 用户系统
- 注册 / 登录 / 刷新 Token / 登出  
- JWT 鉴权  
- session 管理  

---

### 8.2 分析任务系统
- 提交分析任务  
- 查询任务状态  
- 获取分析报告  

---

### 8.3 分析结果结构

输出包含：

- 评论总结（Summary）  
- 问题分类（Categories）  
- 关键词（Keywords）  
- 改进建议（Suggestions）  
- 相似案例（Similar Cases）  

---

## 🚀 九、快速启动

### 1. 配置环境变量

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
````

---

### 2. 启动服务

```bash
docker compose up -d --build
```

---

### 3. 访问服务

* 后端文档：[http://localhost:8000/docs](http://localhost:8000/docs)
* 前端页面：[http://localhost:5173](http://localhost:5173)
* 健康检查：[http://localhost:8000/health](http://localhost:8000/health)

---

## 🔐 十、默认账号

```
username: admin
password: Admin@123456
```

可在 `.env` 中修改：

* DEFAULT_ADMIN_USERNAME
* DEFAULT_ADMIN_PASSWORD
* DEFAULT_ADMIN_EMAIL

---

## 🧪 十一、测试

### 后端测试

```bash
docker compose exec api bash -lc "pytest"
```

---

### 前端构建

```bash
docker compose exec frontend npm run build
```

---

## 📁 十二、项目结构

```
review-agent/
├─ app/
│  ├─ core/          # 配置 / LangGraph / RAG
│  ├─ crud/          # 数据库操作
│  ├─ models/        # ORM模型
│  ├─ routers/       # API路由
│  ├─ services/      # 业务逻辑
│  └─ utils/         # 工具函数
├─ frontend/
│  ├─ src/api/       # 请求封装
│  ├─ src/types/     # 类型定义
│  └─ src/App.vue
├─ tests/
├─ docker-compose.yml
└─ requirements.txt
```
