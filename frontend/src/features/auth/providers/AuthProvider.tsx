import { useEffect, useState, type PropsWithChildren } from 'react'

import { getMe } from '../api'
import { clearCurrentUserCache, getCachedCurrentUser, saveCurrentUser } from '../authCache'
import { CurrentUserContext, type CurrentUserState } from './authContext'

export function AuthProvider({ children }: PropsWithChildren) {
  const [state, setState] = useState<CurrentUserState>(() => {
    const cachedUser = getCachedCurrentUser()

    return {
      error: null,
      isLoading: cachedUser === null,
      user: cachedUser,
    }
  })

  useEffect(() => {
    let isMounted = true

    getMe()
      .then((user) => {
        if (!isMounted) {
          return
        }

        saveCurrentUser(user)
        setState({ error: null, isLoading: false, user })
      })
      .catch((currentError: unknown) => {
        if (!isMounted) {
          return
        }

        clearCurrentUserCache()
        setState({
          error:
            currentError instanceof Error
              ? currentError
              : new Error('Unable to load current user'),
          isLoading: false,
          user: null,
        })
      })

    return () => {
      isMounted = false
    }
  }, [])

  return (
    <CurrentUserContext.Provider value={state}>
      {children}
    </CurrentUserContext.Provider>
  )
}
