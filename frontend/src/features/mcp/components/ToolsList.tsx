import { Link } from 'react-router-dom'

import type { McpTool } from '../types'

type Props = {
  serverName: string
  tools: McpTool[]
}

export function ToolsList({ serverName, tools }: Props) {
  return (
    <ul className="m-0 grid gap-1 p-0 text-sm text-slate-600">
      {tools.map((tool) => (
        <li className="list-none" key={tool.name}>
          <Link
            className="font-medium text-blue-700 no-underline hover:text-blue-900 hover:underline"
            to={`/mcp/${encodeURIComponent(serverName)}/tools/${encodeURIComponent(tool.name)}`}
          >
            {tool.name}
          </Link>
        </li>
      ))}
    </ul>
  )
}
