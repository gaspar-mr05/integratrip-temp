import { API_BASE_URL, requestJson } from '../../../shared/api'
import type { CurrentUser } from '../types'

export function login(): void {
  window.location.assign(`${API_BASE_URL}/auth/login`)
}

export function logout(): void {
  window.location.assign(`${API_BASE_URL}/auth/logout`)
}

export function getMe(): Promise<CurrentUser> {
  return requestJson<CurrentUser>('/auth/me')
}
