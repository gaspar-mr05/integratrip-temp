import { useCallback, useState } from 'react'

import { listServerTools } from '../api'
import { getCachedTools, saveTools } from '../mcpCache'
import type { McpTool } from '../types'

type McpToolsState = {
  error: Error | null
  isLoading: boolean
  tools: McpTool[]
}

export function useMcpTools(initialServerName?: string) {
  const [state, setState] = useState<McpToolsState>(() => {
    const cachedTools = initialServerName
      ? getCachedTools(initialServerName)
      : null

    return {
      error: null,
      isLoading: initialServerName !== undefined && cachedTools === null,
      tools: cachedTools?.value ?? [],
    }
  })

  const fetchTools = useCallback(async (serverName: string): Promise<void> => {
    const cachedTools = getCachedTools(serverName)

    if (cachedTools?.isFresh) {
      setState({ error: null, isLoading: false, tools: cachedTools.value })
      return
    }

    setState((currentState) => ({
      ...currentState,
      error: null,
      isLoading: cachedTools === null,
    }))

    try {
      const response = await listServerTools(serverName)
      saveTools(serverName, response.tools)
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
  }, [])

  return {
    error: state.error,
    fetchTools,
    isLoading: state.isLoading,
    tools: state.tools,
  }
}
