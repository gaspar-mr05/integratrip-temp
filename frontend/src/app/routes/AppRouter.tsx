import { Navigate, Route, Routes, useParams } from 'react-router-dom'

import { ChatPage } from '../../features/chat/pages'
import { McpPage, McpToolPage } from '../../features/mcp/pages'
import { AppLayout } from '../layouts/AppLayout'
import { LandingPage } from '../pages'
import { ProtectedRoute } from './ProtectedRoute'

function LegacyMcpToolRedirect() {
  const { serverName, toolName } = useParams<{
    serverName: string
    toolName: string
  }>()

  if (!serverName || !toolName) {
    return <Navigate replace to="/config" />
  }

  return (
    <Navigate
      replace
      to={`/config/mcp/${encodeURIComponent(serverName)}/tools/${encodeURIComponent(toolName)}`}
    />
  )
}

export function AppRouter() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <AppLayout>
            <LandingPage />
          </AppLayout>
        }
      />
      <Route
        path="/chat"
        element={
          <AppLayout fullBleed>
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          </AppLayout>
        }
      />
      <Route
        path="/config"
        element={
          <AppLayout>
            <ProtectedRoute>
              <McpPage />
            </ProtectedRoute>
          </AppLayout>
        }
      />
      <Route
        path="/config/mcp/:serverName/tools/:toolName"
        element={
          <AppLayout>
            <ProtectedRoute>
              <McpToolPage />
            </ProtectedRoute>
          </AppLayout>
        }
      />
      <Route path="/mcp" element={<Navigate replace to="/config" />} />
      <Route
        path="/mcp/:serverName/tools/:toolName"
        element={<LegacyMcpToolRedirect />}
      />
    </Routes>
  )
}
