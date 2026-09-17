import { SendIcon } from './icons'

export function MessageComposer() {
  return (
    <div className="px-4 pb-4 sm:px-8 sm:pb-6">
      <div className="mx-auto flex max-w-3xl items-end gap-3 rounded-xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-slate-400">
        <textarea
          aria-label="Mensaje"
          className="max-h-36 min-h-11 flex-1 resize-none border-0 bg-transparent px-3 py-2.5 text-sm leading-6 text-slate-900 outline-none placeholder:text-slate-400"
          placeholder="Escribe un mensaje..."
          rows={1}
        />
        <button
          aria-label="Enviar mensaje"
          className="grid size-11 shrink-0 cursor-pointer place-items-center rounded-lg border-0 bg-blue-700 text-white transition-colors hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          type="button"
        >
          <SendIcon />
        </button>
      </div>
      <p className="mx-auto mt-2 mb-0 max-w-3xl text-center text-xs text-slate-400">
        Vista preliminar · El envío de mensajes estará disponible próximamente.
      </p>
    </div>
  )
}
