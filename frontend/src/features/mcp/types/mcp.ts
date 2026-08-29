export type McpTool = {
  name: string
  description?: string
  inputSchema?: unknown
}

export type ListServerToolsResponse = {
  tools: McpTool[]
}

export type CallServerToolResponse = {
  output: unknown
}

export type McpConnectionStatus = 'connected' | 'disconnected'

export type McpConnectionStatusResponse = {
  connected: boolean
  status: McpConnectionStatus
}

export type ToolArguments = Record<string, unknown>
