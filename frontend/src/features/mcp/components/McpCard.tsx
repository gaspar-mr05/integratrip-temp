import { Button, ErrorMessage, Skeleton } from '../../../shared/ui'
import { useMcpConnection, useMcpTools } from '../hooks'
import type { McpConnectionDisplayStatus } from '../types'
import { ToolsList } from './ToolsList'
import { ToolsListSkeleton } from './ToolsListSkeleton'

type Props = {
  index: number
  serverName: string
  serverApiName: string
  status: McpConnectionDisplayStatus
}

export const McpCard = ({ index, serverName, serverApiName, status }: Props) => {
  const { connectMcpServer } = useMcpConnection()
  const { error, fetchTools, isLoading, tools } = useMcpTools()

  const hasTools = tools.length > 0
  const isChecking = status === 'checking'
  const hasStatusError = status === 'error'

  return (
    <article className="flex min-h-56 flex-col justify-between gap-6 border-t border-slate-300 py-5 transition-colors hover:border-slate-950">
      <div className="grid gap-4">
        <div className="flex items-center justify-between gap-3">
          <span className="text-xs font-semibold tracking-[0.14em] text-slate-400">0{index}</span>
          <span
            aria-live="polite"
            className={`inline-flex items-center gap-1.5 text-xs font-medium ${status === 'connected' ? 'text-emerald-700' : hasStatusError ? 'text-red-700' : 'text-slate-500'}`}
          >
            <span
              className={`size-1.5 rounded-full ${status === 'connected' ? 'bg-emerald-600' : isChecking ? 'animate-pulse bg-blue-500' : hasStatusError ? 'bg-red-600' : 'bg-slate-400'}`}
            />
            {status === 'connected'
              ? 'Conectado'
              : isChecking
                ? 'Comprobando…'
                : hasStatusError
                  ? 'No disponible'
                : 'Sin conectar'}
          </span>
        </div>
        <div>
          <h2 className="m-0 text-2xl leading-tight font-semibold tracking-[-0.03em] text-slate-950">
            {serverName}
          </h2>
          <p className="mt-2 mb-0 text-sm text-slate-500">{serverApiName}</p>
        </div>
      </div>

      {status === 'connected' ? (
        <div className="grid gap-3">
          <Button className="w-full sm:w-fit" onClick={() => fetchTools(serverApiName)}>
            Ver tools
          </Button>

          {isLoading ? (
            <ToolsListSkeleton />
          ) : hasTools ? (
            <ToolsList serverName={serverApiName} tools={tools} />
          ) : null}

          {error ? (
            <ErrorMessage message={error.message} />
          ) : null}
        </div>
      ) : status === 'disconnected' ? (
        <Button
          className="w-full sm:w-fit"
          onClick={() => connectMcpServer(serverApiName)}
        >
          Conectar
        </Button>
      ) : isChecking ? (
        <Skeleton className="h-10 w-full sm:w-28" />
      ) : (
        <ErrorMessage message="No se pudo comprobar el estado de conexión." />
      )}
    </article>
  )
}
