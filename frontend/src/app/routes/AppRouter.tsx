import { AppLayout } from '../layouts/AppLayout'
import { McpPage } from '../../features/mcp/pages'

export function AppRouter() {
  return (
    <AppLayout>
      <McpPage />
    </AppLayout>
  )
}
