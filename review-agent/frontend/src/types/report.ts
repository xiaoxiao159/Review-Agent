export type TaskStatus = "pending" | "running" | "completed" | "failed"

export interface AnalyzeRequest {
  product_id: string
  date_range?: {
    start: string
    end: string
  }
}

export interface AnalyzeResponse {
  task_id: string
}

export interface TaskStatusResponse {
  task_id: string
  status: TaskStatus
}

export interface Summary {
  total_count: number
  negative_count: number
  negative_rate: number
  avg_sentiment: number
}

export interface SentimentTrendItem {
  month: string
  avg_sentiment: number
}

export interface SimilarCase {
  review_id: string
  content: string
  similarity_score: number
}

export interface ReportResponse {
  summary: Summary
  reason_categories: Record<string, number>
  keywords: string[]
  sentiment_trend: SentimentTrendItem[]
  suggestions: string[]
  similar_cases: SimilarCase[]
}
