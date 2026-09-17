import type { FunctionCall } from '../types'
import { formatJson } from '../utils'

type AssistantMessageProps = {
  functionCalls: readonly FunctionCall[]
  text: string
}

export function AssistantMessage({
  functionCalls,
  text,
}: AssistantMessageProps) {
  return (
    <article className="grid justify-items-start gap-3" aria-label="Respuesta del asistente">
      {text.trim() ? (
        <p className="m-0 max-w-[90%] whitespace-pre-wrap break-words rounded-xl rounded-bl-sm border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-800 shadow-sm sm:max-w-[80%]">
          {text}
        </p>
      ) : null}

      {functionCalls.map((functionCall) => (
        <section
          className="w-full max-w-2xl overflow-hidden rounded-lg border border-amber-200 bg-amber-50"
          key={functionCall.id}
        >
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200 px-3 py-2">
            <span className="text-xs font-semibold tracking-wide text-amber-800 uppercase">
              Tool solicitada
            </span>
            <code className="text-xs font-semibold text-slate-700">
              {functionCall.name}
            </code>
          </div>
          <pre className="m-0 max-h-64 overflow-auto whitespace-pre-wrap break-words p-3 text-xs leading-5 text-slate-700">
            {formatJson(functionCall.arguments_json)}
          </pre>
        </section>
      ))}
    </article>
  )
}
