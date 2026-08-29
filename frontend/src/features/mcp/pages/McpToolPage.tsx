import { useEffect } from 'react'
import { useParams } from 'react-router-dom'

import { ErrorMessage } from '../../../shared/ui'
import {
  ToolExecutionResult,
  ToolForm,
  ToolFormSkeleton,
  ToolPageHeader,
} from '../components'
import { useMcpTools, useToolExecution } from '../hooks'

export function McpToolPage() {
  const { serverName, toolName } = useParams<{
    serverName: string
    toolName: string
  }>()
  const { error, fetchTools, isLoading, tools } = useMcpTools(serverName)
  const { error: executionError, execute, isSubmitting, result } = useToolExecution()
  const tool = tools.find((currentTool) => currentTool.name === toolName)

  useEffect(() => {
    if (serverName) {
      void fetchTools(serverName)
    }
  }, [fetchTools, serverName])

  if (!serverName || !toolName) {
    return <ErrorMessage message="Ruta inválida." />
  }

  return (
    <section className="mx-auto grid w-full max-w-4xl gap-10">
      <ToolPageHeader tool={tool} toolName={toolName} />

      <div className="border-y border-slate-300 py-7 sm:py-8">
        {isLoading ? (
          <ToolFormSkeleton />
        ) : error ? (
          <ErrorMessage message={error.message} />
        ) : tool ? (
          <ToolForm
            inputSchema={tool.inputSchema ?? tool.input_schema}
            isSubmitting={isSubmitting}
            key={tool.name}
            onSubmit={(argumentsValue) => execute(serverName, toolName, argumentsValue)}
          />
        ) : (
          <ErrorMessage message="Tool no encontrada." />
        )}
      </div>

      {executionError ? <ErrorMessage message={executionError.message} /> : null}

      {result ? <ToolExecutionResult result={result} /> : null}
    </section>
  )
}
