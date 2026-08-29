import { useEffect, useState } from 'react'

import { getMe } from '../api'
import type { CurrentUser } from '../types'

type CurrentUserState = {
  error: Error | null
  isLoading: boolean
  user: CurrentUser | null
}

export function useCurrentUser(): CurrentUserState {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let isMounted = true

    getMe()
      .then((currentUser) => {
        if (!isMounted) {
          return
        }

        setUser(currentUser)
        setError(null)
      })
      .catch((currentError: unknown) => {
        if (!isMounted) {
          return
        }

        setUser(null)
        setError(
          currentError instanceof Error
            ? currentError
            : new Error('Unable to load current user'),
        )
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  return { error, isLoading, user }
}
