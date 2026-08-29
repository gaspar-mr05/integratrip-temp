import { connectMcpServer } from '../api'
import { invalidateMcpServerCache } from '../mcpCache'

export function useMcpConnection() {
  function connect(serverName: string): void {
    invalidateMcpServerCache(serverName)
    connectMcpServer(serverName)
  }

  return { connectMcpServer: connect }
}
