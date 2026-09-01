import { McpCard } from '../components'
import { useMcpConnectionStatuses } from '../hooks'

type McpServerViewModel = {
  serverName: string
  serverApiName: string
}

const mcpServers: McpServerViewModel[] = [
  {
    serverName: 'Andes Air',
    serverApiName: 'andes-air',
  },
  {
    serverName: 'StayWell',
    serverApiName: 'staywell',
  },
  {
    serverName: 'Cielo Sur',
    serverApiName: 'cielo-sur',
  },
]

const mcpServerApiNames = mcpServers.map((server) => server.serverApiName)

export function McpPage() {
  const statuses = useMcpConnectionStatuses(mcpServerApiNames)

  return (
    <section className="mx-auto grid w-full max-w-7xl gap-12">
      <div className="grid max-w-2xl gap-3">
        <p className="m-0 text-sm font-semibold tracking-[0.16em] text-blue-700 uppercase">
          Directorio
        </p>
        <h1 className="m-0 text-4xl leading-none font-semibold tracking-[-0.04em] text-slate-950 md:text-6xl">
          Servidores MCP
        </h1>
        <p className="m-0 text-base leading-7 text-slate-600">
          Conecta un servidor para listar y ejecutar sus tools.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2 lg:grid-cols-3">
        {mcpServers.map((server, index) => (
          <McpCard
            index={index + 1}
            key={server.serverName}
            serverName={server.serverName}
            serverApiName={server.serverApiName}
            status={statuses[server.serverApiName] ?? 'checking'}
          />
        ))}
      </div>
    </section>
  )
}
