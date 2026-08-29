import { Link } from 'react-router-dom'

import type { McpTool } from '../types'

type Props = {
  serverName: string
  tools: McpTool[]
}

export function ToolsList({ serverName, tools }: Props) {
  return (
    <ul className="m-0 grid divide-y divide-slate-200 border-t border-slate-200 p-0">
      {tools.map((tool) => (
        <li className="list-none" key={tool.name}>
          <Link
            className="group flex items-center justify-between gap-3 py-2.5 font-medium text-slate-700 no-underline transition-colors hover:text-blue-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            to={`/mcp/${encodeURIComponent(serverName)}/tools/${encodeURIComponent(tool.name)}`}
          >
            {tool.name}
            <span aria-hidden="true" className="text-slate-400 transition-transform group-hover:translate-x-0.5 group-hover:text-blue-700">→</span>
          </Link>
        </li>
      ))}
    </ul>
  )
}
