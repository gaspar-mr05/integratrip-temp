import { Link } from 'react-router-dom'

import type { McpTool } from '../types'

type ToolPageHeaderProps = {
  tool: McpTool | undefined
  toolName: string
}

export function ToolPageHeader({ tool, toolName }: ToolPageHeaderProps) {
  return (
    <div className="grid max-w-3xl gap-3">
      <Link
        className="inline-flex w-fit items-center gap-2 text-sm font-medium text-slate-600 no-underline transition-colors hover:text-blue-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        to="/mcp"
      >
        <span aria-hidden="true">←</span> Volver a servidores
      </Link>
      <p className="m-0 text-sm font-semibold tracking-[0.16em] text-blue-700 uppercase">
        Tool
      </p>
      <h1 className="m-0 break-words text-4xl leading-tight font-semibold tracking-[-0.04em] text-slate-950 sm:text-5xl">
        {toolName}
      </h1>
      {tool?.description ? (
        <p className="m-0 text-base leading-7 text-slate-600">
          {tool.description}
        </p>
      ) : null}
    </div>
  )
}
