import { ChatIcon } from './icons'

export function ChatEmptyState() {
  return (
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
  )
}
