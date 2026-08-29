import { Button } from '../../../shared/ui'
import { useMcpConnection, useMcpTools } from '../hooks'
import type { McpConnectionStatus } from '../types'
import { ToolsList } from './ToolsList'

type Props = {
  serverName: string
  serverApiName: string
  status: McpConnectionStatus
}

export const McpCard = ({ serverName, serverApiName, status }: Props) => {
  const { connectMcpServer } = useMcpConnection()
  const { error, fetchTools, isLoading, tools } = useMcpTools()

  const hasTools = tools.length > 0

  return (
    <article className="flex min-h-40 flex-col justify-between gap-4 rounded-lg border border-slate-200 bg-white p-5">
      <h2 className="m-0 text-xl leading-tight font-semibold text-slate-950">
        {serverName}
      </h2>

      {status === 'connected' ? (
        <div className="grid gap-3">
          <Button onClick={() => fetchTools(serverApiName)}>
            {isLoading ? 'Cargando...' : 'Ver tools'}
          </Button>

          {hasTools ? (
            <ToolsList serverName={serverApiName} tools={tools} />
          ) : null}

          {error ? (
            <p className="m-0 text-sm text-red-600">{error.message}</p>
          ) : null}
        </div>
      ) : (
        <Button onClick={() => connectMcpServer(serverApiName)}>Conectar</Button>
      )}
    </article>
  )
}

