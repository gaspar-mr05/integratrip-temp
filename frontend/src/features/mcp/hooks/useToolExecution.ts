import { useCallback, useState } from 'react'

import { callServerTool } from '../api'
import type { CallServerToolResponse, ToolArguments } from '../types'

type ToolExecutionState = {
  error: Error | null
  isSubmitting: boolean
  result: CallServerToolResponse | null
}

export function useToolExecution() {
  const [state, setState] = useState<ToolExecutionState>({
    error: null,
    isSubmitting: false,
    result: null,
  })

  const execute = useCallback(async (
    serverName: string,
    toolName: string,
    argumentsValue: ToolArguments,
  ): Promise<void> => {
    setState({ error: null, isSubmitting: true, result: null })

    try {
      const result = await callServerTool(serverName, toolName, argumentsValue)
      setState({ error: null, isSubmitting: false, result })
    } catch (error) {
      setState({
        error: error instanceof Error ? error : new Error('No se pudo ejecutar la tool'),
        isSubmitting: false,
        result: null,
      })
    }
  }, [])

  return { ...state, execute }
}
