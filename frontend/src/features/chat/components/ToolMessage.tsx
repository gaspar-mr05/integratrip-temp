import type { FunctionResult } from '../types'
import { formatJson } from '../utils'

type ToolMessageProps = {
  functionResults: readonly FunctionResult[]
}

export function ToolMessage({ functionResults }: ToolMessageProps) {
  return (
    <article className="grid gap-3" aria-label="Resultados de tools">
      {functionResults.map((result) => (
        <section
          className={`w-full max-w-2xl overflow-hidden rounded-lg border ${result.is_error ? 'border-red-200 bg-red-50' : 'border-emerald-200 bg-emerald-50'}`}
          key={result.id}
        >
          <div
            className={`flex flex-wrap items-center justify-between gap-2 border-b px-3 py-2 ${result.is_error ? 'border-red-200' : 'border-emerald-200'}`}
          >
            <span
              className={`text-xs font-semibold tracking-wide uppercase ${result.is_error ? 'text-red-700' : 'text-emerald-700'}`}
            >
              {result.is_error ? 'Error de tool' : 'Resultado de tool'}
            </span>
            <code className="text-xs font-semibold text-slate-700">
              {result.name}
            </code>
          </div>
          <pre className="m-0 max-h-64 overflow-auto whitespace-pre-wrap break-words p-3 text-xs leading-5 text-slate-700">
            {formatJson(result.result_json)}
          </pre>
        </section>
      ))}
    </article>
  )
}
