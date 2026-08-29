import { createContext, useContext } from 'react'

import type { CurrentUser } from '../types'

export type CurrentUserState = {
  error: Error | null
  isLoading: boolean
  user: CurrentUser | null
}

export const CurrentUserContext = createContext<CurrentUserState | null>(null)

export function useCurrentUserContext(): CurrentUserState {
  const currentUser = useContext(CurrentUserContext)

  if (!currentUser) {
    throw new Error('useCurrentUser must be used within AuthProvider')
  }

  return currentUser
}
