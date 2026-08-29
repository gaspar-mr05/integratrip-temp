import type { PropsWithChildren } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from '../layouts/AppLayout'
import { LandingPage } from '../pages'
import { useCurrentUser } from '../../features/auth/hooks'
import { McpPage, McpToolPage } from '../../features/mcp/pages'

function ProtectedRoute({ children }: PropsWithChildren) {
  const { isLoading, user } = useCurrentUser()

  if (isLoading) {
    return <p className="m-0 text-sm text-slate-600">Cargando...</p>
  }

  if (!user) {
    return <Navigate replace to="/" />
  }

  return children
}

export function AppRouter() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/mcp"
          element={
            <ProtectedRoute>
              <McpPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/mcp/:serverName/tools/:toolName"
          element={
            <ProtectedRoute>
              <McpToolPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </AppLayout>
  )
}
