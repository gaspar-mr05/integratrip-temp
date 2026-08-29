import { Route, Routes } from 'react-router-dom'

import { AppLayout } from '../layouts/AppLayout'
import { LandingPage } from '../pages'
import { McpPage, McpToolPage } from '../../features/mcp/pages'

export function AppRouter() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/mcp" element={<McpPage />} />
        <Route
          path="/mcp/:serverName/tools/:toolName"
          element={<McpToolPage />}
        />
      </Routes>
    </AppLayout>
  )
}
