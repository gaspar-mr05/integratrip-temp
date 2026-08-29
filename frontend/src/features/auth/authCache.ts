import { readSessionCache, removeSessionCache, writeSessionCache } from '../../shared/lib/sessionCache'
import type { CurrentUser } from './types'

const CURRENT_USER_CACHE_KEY = 'integratrip:current-user'
const CURRENT_USER_CACHE_TTL = 15 * 60 * 1000

function isCurrentUser(value: unknown): value is CurrentUser {
  return (
    typeof value === 'object' &&
    value !== null &&
    'user_id' in value &&
    typeof value.user_id === 'string'
  )
}

export function getCachedCurrentUser(): CurrentUser | null {
  const cachedUser = readSessionCache(
    CURRENT_USER_CACHE_KEY,
    CURRENT_USER_CACHE_TTL,
    isCurrentUser,
  )

  return cachedUser?.isFresh ? cachedUser.value : null
}

export function saveCurrentUser(user: CurrentUser): void {
  writeSessionCache(CURRENT_USER_CACHE_KEY, user)
}

export function clearCurrentUserCache(): void {
  removeSessionCache(CURRENT_USER_CACHE_KEY)
}
