
import type { McpTool } from '../types'

type Props = {
  tools: McpTool[]
}

export function ToolsList({ tools }: Props) {
  return (
    <ul className="m-0 grid gap-1 p-0 text-sm text-slate-600">
      {tools.map((tool) => (
        <li className="list-none" key={tool.name}>
          {tool.name}
        </li>
      ))}
    </ul>
  )
}
