export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenPairResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserProfileResponse {
  id: string
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
}
