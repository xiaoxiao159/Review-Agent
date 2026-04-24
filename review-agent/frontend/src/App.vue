<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import VChart from "vue-echarts"
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { LineChart } from "echarts/charts"
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components"
import { analyzeReviews, getMe, getReport, getTaskStatus, isAuthenticated, login, logout, register } from "./api/client"
import type { UserProfileResponse } from "./types/auth"
import type { ReportResponse, TaskStatus } from "./types/report"

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const productId = ref("")
const startDate = ref("")
const endDate = ref("")
const taskId = ref("")
const status = ref<TaskStatus | "idle">("idle")
const loading = ref(false)
const error = ref("")
const report = ref<ReportResponse | null>(null)
const user = ref<UserProfileResponse | null>(null)
const authMode = ref<"login" | "register">("login")

const authUsername = ref("")
const authEmail = ref("")
const authPassword = ref("")
const authBusy = ref(false)

let timer: ReturnType<typeof setInterval> | null = null

const trendOption = computed(() => {
  if (!report.value) return {}
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 36, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: "category",
      data: report.value.sentiment_trend.map((i) => i.month),
      boundaryGap: false
    },
    yAxis: { type: "value", min: 0, max: 1 },
    series: [
      {
        name: "avg_sentiment",
        type: "line",
        smooth: true,
        areaStyle: { opacity: 0.15 },
        lineStyle: { width: 3 },
        data: report.value.sentiment_trend.map((i) => i.avg_sentiment)
      }
    ]
  }
})

const statusText = computed(() => {
  if (status.value === "idle") return "未开始"
  if (status.value === "pending") return "排队中"
  if (status.value === "running") return "执行中"
  if (status.value === "completed") return "已完成"
  return "失败"
})

const statusClass = computed(() => `status-badge status-${status.value}`)
const loggedIn = computed(() => !!user.value)

function clearPolling() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

async function loadMe() {
  if (!isAuthenticated()) return
  try {
    user.value = await getMe()
  } catch {
    user.value = null
  }
}

async function handleLogin() {
  error.value = ""
  authBusy.value = true
  try {
    await login({ username: authUsername.value.trim(), password: authPassword.value })
    await loadMe()
    authPassword.value = ""
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "登录失败"
  } finally {
    authBusy.value = false
  }
}

async function handleRegister() {
  error.value = ""
  authBusy.value = true
  try {
    await register({
      username: authUsername.value.trim(),
      email: authEmail.value.trim(),
      password: authPassword.value,
    })
    authMode.value = "login"
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "注册失败"
  } finally {
    authBusy.value = false
  }
}

async function handleLogout() {
  clearPolling()
  await logout()
  user.value = null
  report.value = null
  taskId.value = ""
  status.value = "idle"
}

async function fetchReport() {
  if (!taskId.value) return
  report.value = await getReport(taskId.value)
}

async function pollStatus() {
  if (!taskId.value) return
  const res = await getTaskStatus(taskId.value)
  status.value = res.status
  if (res.status === "completed") {
    clearPolling()
    await fetchReport()
    loading.value = false
  }
  if (res.status === "failed") {
    clearPolling()
    loading.value = false
    error.value = "任务执行失败"
  }
}

async function submitAnalyze() {
  error.value = ""
  report.value = null
  loading.value = true
  clearPolling()

  try {
    if (!productId.value.trim()) throw new Error("请先输入 product_id")

    const payload: { product_id: string; date_range?: { start: string; end: string } } = {
      product_id: productId.value.trim()
    }

    if (startDate.value && endDate.value) {
      payload.date_range = { start: startDate.value, end: endDate.value }
    }

    const res = await analyzeReviews(payload)
    taskId.value = res.task_id
    status.value = "pending"

    await pollStatus()
    timer = setInterval(async () => {
      try {
        await pollStatus()
      } catch (e: any) {
        clearPolling()
        loading.value = false
        error.value = e?.response?.data?.detail || e?.message || "轮询失败"
      }
    }, 2000)
  } catch (e: any) {
    loading.value = false
    error.value = e?.response?.data?.detail || e?.message || "请求失败"
  }
}

onMounted(async () => {
  await loadMe()
})

onBeforeUnmount(() => clearPolling())
</script>

<template>
  <main class="page">
    <header class="hero">
      <div>
        <h1>Review Agent Dashboard</h1>
        <p>账号登录后提交分析任务，自动轮询并可视化展示趋势与相似案例。</p>
      </div>
      <div :class="statusClass">{{ statusText }}</div>
    </header>

    <section v-if="!loggedIn" class="card token-card">
      <div class="card-title">账号认证中心</div>
      <div class="switcher">
        <button class="btn" :class="authMode === 'login' ? 'btn-primary' : 'btn-secondary'" @click="authMode = 'login'">登录</button>
        <button class="btn" :class="authMode === 'register' ? 'btn-primary' : 'btn-secondary'" @click="authMode = 'register'">注册</button>
      </div>

      <div class="form-grid">
        <label>
          <span>用户名</span>
          <input v-model="authUsername" placeholder="请输入用户名" />
        </label>
        <label v-if="authMode === 'register'">
          <span>邮箱</span>
          <input v-model="authEmail" placeholder="请输入邮箱" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="authPassword" type="password" placeholder="请输入密码" />
        </label>
      </div>

      <div class="actions">
        <button v-if="authMode === 'login'" class="btn btn-primary" :disabled="authBusy" @click="handleLogin">{{ authBusy ? "登录中..." : "登录" }}</button>
        <button v-else class="btn btn-primary" :disabled="authBusy" @click="handleRegister">{{ authBusy ? "注册中..." : "注册" }}</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section v-else class="card">
      <div class="card-title">当前账号</div>
      <div class="meta">
        <p><strong>用户名：</strong>{{ user?.username }}</p>
        <p><strong>角色：</strong>{{ user?.role }}</p>
      </div>
      <div class="actions">
        <button class="btn btn-secondary" @click="handleLogout">退出登录</button>
      </div>
    </section>

    <section v-if="loggedIn" class="card">
      <div class="card-title">提交分析任务</div>
      <div class="form-grid">
        <label>
          <span>Product ID</span>
          <input v-model="productId" placeholder="例如：p001" />
        </label>
        <label>
          <span>开始日期</span>
          <input v-model="startDate" type="date" />
        </label>
        <label>
          <span>结束日期</span>
          <input v-model="endDate" type="date" />
        </label>
      </div>

      <div class="actions">
        <button class="btn btn-primary" :disabled="loading" @click="submitAnalyze">
          {{ loading ? "分析中..." : "开始分析" }}
        </button>
      </div>

      <div class="meta">
        <p><strong>Task ID：</strong>{{ taskId || "-" }}</p>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section v-if="loggedIn && report" class="card">
      <div class="card-title">分析报告</div>
      <div class="metric-grid">
        <div class="metric-item"><div class="metric-label">总评论</div><div class="metric-value">{{ report.summary.total_count }}</div></div>
        <div class="metric-item"><div class="metric-label">差评数</div><div class="metric-value">{{ report.summary.negative_count }}</div></div>
        <div class="metric-item"><div class="metric-label">差评率</div><div class="metric-value">{{ (report.summary.negative_rate * 100).toFixed(1) }}%</div></div>
        <div class="metric-item"><div class="metric-label">平均情感分</div><div class="metric-value">{{ report.summary.avg_sentiment.toFixed(3) }}</div></div>
      </div>

      <div class="split-grid">
        <div>
          <h3>原因分类</h3>
          <ul class="list"><li v-for="(count, key) in report.reason_categories" :key="key"><span>{{ key }}</span><strong>{{ count }}</strong></li></ul>
        </div>
        <div>
          <h3>关键词</h3>
          <div class="chips"><span v-for="item in report.keywords" :key="item" class="chip">{{ item }}</span></div>
          <h3 class="mt">改进建议</h3>
          <ul class="list bullets"><li v-for="item in report.suggestions" :key="item">{{ item }}</li></ul>
        </div>
      </div>

      <h3>情感趋势</h3>
      <VChart class="chart" :option="trendOption" autoresize />

      <h3>相似案例</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>review_id</th><th>content</th><th>similarity_score</th></tr></thead>
          <tbody><tr v-for="item in report.similar_cases" :key="item.review_id"><td>{{ item.review_id }}</td><td>{{ item.content }}</td><td>{{ item.similarity_score.toFixed(4) }}</td></tr></tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page { max-width: 1100px; margin: 24px auto; padding: 0 16px 24px; font-family: Inter, "PingFang SC", "Microsoft YaHei", sans-serif; color: #1a2240; }
.hero { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; background: linear-gradient(135deg, #1e2b5f, #3f63d8); color: #fff; border-radius: 16px; padding: 22px; margin-bottom: 16px; box-shadow: 0 12px 24px rgba(35, 63, 145, 0.22); }
.hero h1 { margin: 0 0 8px; font-size: 28px; line-height: 1.2; }
.hero p { margin: 0; opacity: 0.9; }
.card { background: #fff; border: 1px solid #e7ebf5; border-radius: 14px; padding: 18px; margin-bottom: 16px; box-shadow: 0 8px 18px rgba(21, 41, 96, 0.06); }
.card-title { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
input { width: 100%; border: 1px solid #d5ddee; border-radius: 10px; padding: 10px 12px; font-size: 14px; box-sizing: border-box; background: #fbfcff; }
input:focus { outline: none; border-color: #4d6bda; box-shadow: 0 0 0 3px rgba(76, 108, 221, 0.12); }
.form-grid { display: grid; grid-template-columns: repeat(3, minmax(120px, 1fr)); gap: 12px; }
label span { display: block; font-size: 12px; color: #5f6c8c; margin-bottom: 6px; }
.actions { margin-top: 12px; display: flex; gap: 10px; }
.btn { border: 0; border-radius: 10px; padding: 10px 16px; font-weight: 600; cursor: pointer; }
.btn-primary { background: #3f63d8; color: #fff; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #edf2ff; color: #27366e; }
.meta { margin-top: 8px; color: #45517a; }
.switcher { display: flex; gap: 8px; margin-bottom: 12px; }
.status-badge { border-radius: 999px; padding: 6px 12px; font-size: 13px; font-weight: 700; white-space: nowrap; }
.status-idle { background: rgba(255, 255, 255, 0.22); color: #fff; }
.status-pending { background: #ffe9b5; color: #7c5200; }
.status-running { background: #cce2ff; color: #174483; }
.status-completed { background: #cbf2d9; color: #0b5a2e; }
.status-failed { background: #ffd6d4; color: #8d1410; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 10px; margin-bottom: 14px; }
.metric-item { background: #f6f8ff; border: 1px solid #dfe6fa; border-radius: 12px; padding: 12px; }
.metric-label { font-size: 12px; color: #5b6789; margin-bottom: 6px; }
.metric-value { font-size: 20px; font-weight: 700; }
.split-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.list { list-style: none; padding: 0; margin: 0; }
.list li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px dashed #dde4f5; }
.bullets li { display: list-item; list-style: disc inside; border-bottom: 0; padding: 4px 0; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { background: #edf3ff; border: 1px solid #d8e5ff; color: #27488f; border-radius: 999px; padding: 4px 10px; font-size: 13px; }
.mt { margin-top: 14px; }
.chart { width: 100%; height: 340px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; }
th, td { border-bottom: 1px solid #e7ebf5; padding: 10px; text-align: left; font-size: 14px; }
th { color: #5a6686; font-weight: 600; background: #f8faff; }
.error { color: #c62828; margin-top: 10px; font-weight: 600; }
@media (max-width: 900px) { .form-grid, .metric-grid, .split-grid { grid-template-columns: 1fr; } .hero { flex-direction: column; } }
</style>
