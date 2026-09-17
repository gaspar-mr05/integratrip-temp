export function TypingIndicator() {
  return (
    <div
      aria-label="IntegraTrip está escribiendo"
      aria-live="polite"
      className="flex justify-start"
      role="status"
    >
      <div className="flex items-center gap-1.5 rounded-xl rounded-bl-sm border border-slate-200 bg-white px-4 py-3 shadow-sm">
        <span className="sr-only">IntegraTrip está escribiendo</span>
        <span
          aria-hidden="true"
          className="size-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s] motion-reduce:animate-none"
        />
        <span
          aria-hidden="true"
          className="size-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s] motion-reduce:animate-none"
        />
        <span
          aria-hidden="true"
          className="size-2 animate-bounce rounded-full bg-slate-400 motion-reduce:animate-none"
        />
      </div>
    </div>
  )
}
