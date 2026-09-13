const conversations = [
  'Plan viaje a Patagonia',
  'Hoteles en Puerto Varas',
  'Vuelos a San Pedro',
]

function ChatIcon() {
  return (
    <svg
      aria-hidden="true"
      className="size-4 shrink-0"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      viewBox="0 0 24 24"
    >
      <path
        d="M7.5 18.5 3 21v-5.25A8.5 8.5 0 1 1 7.5 18.5Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function PlusIcon() {
  return (
    <svg
      aria-hidden="true"
      className="size-4 shrink-0"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      <path d="M12 5v14M5 12h14" strokeLinecap="round" />
    </svg>
  )
}

function SendIcon() {
  return (
    <svg
      aria-hidden="true"
      className="size-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      viewBox="0 0 24 24"
    >
      <path
        d="m5 12 14-7-4.75 14-2.8-5.45L5 12Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function ChatPage() {
  return (
    <section
      aria-label="Chat"
      className="grid h-full min-h-0 grid-cols-[4.75rem_minmax(0,1fr)] bg-white sm:grid-cols-[17rem_minmax(0,1fr)]"
    >
      <aside className="flex min-h-0 flex-col border-r border-slate-200 bg-[#f1f1ee] p-3 sm:p-4">
        <button
          className="flex min-h-11 cursor-pointer items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-900 transition-colors hover:border-slate-400 hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:justify-start"
          type="button"
        >
          <PlusIcon />
          <span className="sr-only sm:not-sr-only">Nuevo chat</span>
        </button>

        <div className="mt-7 min-h-0 flex-1 overflow-y-auto">
          <p className="mb-2 hidden px-2 text-xs font-semibold tracking-[0.12em] text-slate-500 uppercase sm:block">
            Conversaciones
          </p>
          <nav aria-label="Conversaciones" className="grid gap-1">
            {conversations.map((conversation, index) => (
              <button
                aria-label={conversation}
                className={`flex min-h-10 cursor-pointer items-center justify-center gap-2 rounded-md border-0 px-3 text-left text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:justify-start ${index === 0 ? 'bg-slate-200 text-slate-950' : 'bg-transparent text-slate-600 hover:bg-slate-200/70 hover:text-slate-950'}`}
                key={conversation}
                type="button"
              >
                <ChatIcon />
                <span className="hidden truncate sm:block">{conversation}</span>
              </button>
            ))}
          </nav>
        </div>
      </aside>

      <div className="flex min-h-0 min-w-0 flex-col bg-[#f7f7f5]">
        <div className="border-b border-slate-200/80 px-5 py-4 sm:px-8">
          <p className="m-0 truncate text-sm font-semibold text-slate-900">
            Plan viaje a Patagonia
          </p>
        </div>

        <div className="grid min-h-0 flex-1 place-items-center overflow-y-auto px-5 py-10 sm:px-8">
          <div className="grid max-w-lg justify-items-center gap-4 text-center">
            <div className="grid size-11 place-items-center rounded-full border border-slate-300 bg-white text-blue-700">
              <ChatIcon />
            </div>
            <div className="grid gap-2">
              <h1 className="m-0 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
                ¿A dónde viajamos?
              </h1>
              <p className="m-0 text-sm leading-6 text-slate-500 sm:text-base">
                Escribe un mensaje para comenzar a planificar tu próximo viaje.
              </p>
            </div>
          </div>
        </div>

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
      </div>
    </section>
  )
}
