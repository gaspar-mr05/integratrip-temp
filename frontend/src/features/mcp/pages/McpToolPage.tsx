import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ToolForm } from '../components'
import { useMcpTools } from '../hooks'
import type { CallServerToolResponse, ToolArguments } from '../types'

export function McpToolPage() {
  const { serverName, toolName } = useParams<{
    serverName: string
    toolName: string
  }>()
  const { error, executeTool, fetchTools, isLoading, tools } = useMcpTools()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<CallServerToolResponse | null>(null)
  const [submitError, setSubmitError] = useState<Error | null>(null)

  useEffect(() => {
    if (serverName) {
      void fetchTools(serverName)
    }
  }, [fetchTools, serverName])

  const tool = useMemo(
    () => tools.find((currentTool) => currentTool.name === toolName),
    [toolName, tools],
  )

  async function handleSubmit(argumentsValue: ToolArguments): Promise<void> {
    if (!serverName || !toolName) {
      return
    }

    setIsSubmitting(true)
    setSubmitError(null)
    setResult(null)

    try {
      const response = await executeTool(serverName, toolName, argumentsValue)
      setResult(response)
    } catch (requestError) {
      setSubmitError(
        requestError instanceof Error
          ? requestError
          : new Error('No se pudo ejecutar la tool'),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!serverName || !toolName) {
    return <p className="m-0 text-sm text-red-600">Ruta inválida.</p>
  }

  return (
    <section className="mx-auto grid w-full max-w-3xl gap-6">
      <div className="grid gap-2">
        <Link
          className="text-sm font-medium text-blue-700 no-underline hover:text-blue-900 hover:underline"
          to="/mcp"
        >
          Volver a servidores
        </Link>
        <h1 className="m-0 text-4xl leading-tight font-bold text-slate-950">
          {toolName}
        </h1>
        {tool?.description ? (
          <p className="m-0 text-slate-600">{tool.description}</p>
        ) : null}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        {isLoading ? (
          <p className="m-0 text-sm text-slate-600">Cargando schema...</p>
        ) : error ? (
          <p className="m-0 text-sm text-red-600">{error.message}</p>
        ) : tool ? (
          <ToolForm
            inputSchema={tool.inputSchema ?? tool.input_schema}
            isSubmitting={isSubmitting}
            key={tool.name}
            onSubmit={handleSubmit}
          />
        ) : (
          <p className="m-0 text-sm text-red-600">Tool no encontrada.</p>
        )}
      </div>

      {submitError ? (
        <p className="m-0 text-sm text-red-600">{submitError.message}</p>
      ) : null}

      {result ? (
        <pre className="overflow-auto rounded-lg border border-slate-200 bg-slate-950 p-4 text-sm text-slate-50">
          {JSON.stringify(result.output, null, 2)}
        </pre>
      ) : null}
    </section>
  )
}
