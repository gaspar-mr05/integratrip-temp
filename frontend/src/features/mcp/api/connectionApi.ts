import { BACKEND_URL, requestJson } from '../../../shared/api'
import type { McpConnectionStatusResponse } from '../types'

export function connectMcpServer(serverName: string): void {
  window.location.assign(`${BACKEND_URL}/mcp/${serverName}/connect`)
}

export function getMcpConnectionStatus(
  serverName: string,
): Promise<McpConnectionStatusResponse> {
  return requestJson<McpConnectionStatusResponse>(`/mcp/${serverName}/status`)
}
