import { useState } from 'react'

import { callServerTool, listServerTools } from '../api'
import type {
  CallServerToolResponse,
  McpTool,
  ToolArguments,
} from '../types'

type McpToolsState = {
  error: Error | null
  isLoading: boolean
  tools: McpTool[]
}

export function useMcpTools() {
  const [state, setState] = useState<McpToolsState>({
    error: null,
    isLoading: false,
    tools: [],
  })

  async function fetchTools(serverName: string): Promise<void> {
    setState((currentState) => ({
      ...currentState,
      error: null,
      isLoading: true,
    }))

    try {
      const response = await listServerTools(serverName)
      setState({ error: null, isLoading: false, tools: response.tools })
    } catch (error) {
      const nextError =
        error instanceof Error ? error : new Error('Unable to fetch MCP tools')

      setState((currentState) => ({
        ...currentState,
        error: nextError,
        isLoading: false,
      }))
    }
  }

  function executeTool(
    serverName: string,
    toolName: string,
    toolArguments: ToolArguments,
  ): Promise<CallServerToolResponse> {
    return callServerTool(serverName, toolName, toolArguments)
  }

  return {
    error: state.error,
    executeTool,
    fetchTools,
    isLoading: state.isLoading,
    tools: state.tools,
  }
}
