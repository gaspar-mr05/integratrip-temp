import type { PendingConfirmation } from '../types'
import { formatJson } from '../utils'

type ConfirmationCardProps = {
  pendingConfirmation: PendingConfirmation
  isDisabled: boolean
  isProcessing: boolean
  onApprove: () => void
  onReject: () => void
}

export function ConfirmationCard({
  pendingConfirmation,
  isDisabled,
  isProcessing,
  onApprove,
  onReject,
}: ConfirmationCardProps) {
  return (
    <article
      aria-busy={isProcessing}
      className="w-full overflow-hidden rounded-xl border border-amber-200 bg-amber-50 shadow-sm"
    >
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200 px-4 py-3">
        <span className="text-xs font-semibold tracking-wide text-amber-800 uppercase">
          Confirmación requerida
        </span>
        <code className="text-xs font-semibold text-slate-700">
          {pendingConfirmation.llm_name}
        </code>
      </header>

      <div className="px-4 py-3">
        <p className="mt-0 mb-2 text-xs font-medium text-slate-600">
          Argumentos
        </p>
        <pre className="m-0 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-white p-3 text-xs leading-5 text-slate-700 ring-1 ring-slate-200">
          {formatJson(pendingConfirmation.arguments_json)}
        </pre>
      </div>

      <footer className="flex flex-wrap items-center justify-end gap-2 border-t border-amber-200 px-4 py-3">
        {isProcessing ? (
          <span className="mr-auto text-xs text-slate-500" aria-live="polite">
            Procesando…
          </span>
        ) : null}
        <button
          className="cursor-pointer rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-500 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isDisabled}
          onClick={onReject}
          type="button"
        >
          Rechazar
        </button>
        <button
          className="cursor-pointer rounded-lg border border-blue-700 bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-300"
          disabled={isDisabled}
          onClick={onApprove}
          type="button"
        >
          Aprobar
        </button>
      </footer>
    </article>
  )
}
