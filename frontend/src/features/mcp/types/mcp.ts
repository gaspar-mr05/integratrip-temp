export type JsonSchemaProperty = {
  const?: unknown
  example?: unknown
  examples?: unknown[]
  default?: unknown
  description?: string
  enum?: unknown[]
  format?: string
  items?: JsonSchemaProperty
  maximum?: number
  maxLength?: number
  minimum?: number
  minLength?: number
  pattern?: string
  properties?: Record<string, JsonSchemaProperty>
  required?: string[]
  title?: string
  type?: string | string[]
}

export type JsonSchemaObject = {
  description?: string
  properties?: Record<string, JsonSchemaProperty>
  required?: string[]
  title?: string
  type?: string
}

export type McpTool = {
  name: string
  description?: string
  input_schema?: JsonSchemaObject
  inputSchema?: JsonSchemaObject
}

export type ListServerToolsResponse = {
  tools: McpTool[]
}

export type CallServerToolResponse = {
  output: unknown
}

export type McpConnectionStatus = 'connected' | 'disconnected'

export type McpConnectionDisplayStatus = McpConnectionStatus | 'checking' | 'error'

export type McpConnectionStatusResponse = {
  connected: boolean
  status: McpConnectionStatus
}

export type ToolArguments = Record<string, unknown>
