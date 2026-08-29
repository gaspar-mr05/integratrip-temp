import type { PropsWithChildren } from 'react'
import { Navigate } from 'react-router-dom'

import { useCurrentUser } from '../../features/auth/hooks'
import { McpPageSkeleton } from '../../features/mcp/components'

export function ProtectedRoute({ children }: PropsWithChildren) {
  const { isLoading, user } = useCurrentUser()

  if (isLoading) {
    return <McpPageSkeleton />
  }

  if (!user) {
    return <Navigate replace to="/" />
  }

  return children
}
