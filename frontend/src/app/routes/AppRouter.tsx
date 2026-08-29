import { Route, Routes } from 'react-router-dom'

import { AppLayout } from '../layouts/AppLayout'
import { LandingPage } from '../pages'
import { McpPage, McpToolPage } from '../../features/mcp/pages'
import { ProtectedRoute } from './ProtectedRoute'

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
