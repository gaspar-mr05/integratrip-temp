import type { FormEvent, KeyboardEvent } from 'react'

import { SendIcon } from './icons'

type MessageComposerProps = {
  disabled: boolean
  isSubmitting: boolean
  onChange: (value: string) => void
  onSubmit: () => Promise<void>
  placeholder?: string
  value: string
}

export function MessageComposer({
  disabled,
  isSubmitting,
  onChange,
  onSubmit,
  placeholder,
  value,
}: MessageComposerProps) {
  const canSubmit = !disabled && !isSubmitting && value.trim().length > 0

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()

    if (canSubmit) {
      void onSubmit()
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()

      if (canSubmit) {
        void onSubmit()
      }
    }
  }

  return (
    <div className="px-4 pb-4 sm:px-8 sm:pb-6">
      <form
        className="mx-auto flex max-w-3xl items-end gap-3 rounded-xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-slate-400"
        onSubmit={handleSubmit}
      >
        <textarea
          aria-label="Mensaje"
          className="max-h-36 min-h-11 flex-1 resize-none border-0 bg-transparent px-3 py-2.5 text-sm leading-6 text-slate-900 outline-none placeholder:text-slate-400"
          disabled={disabled || isSubmitting}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            placeholder ??
            (disabled ? 'Selecciona una conversación...' : 'Escribe un mensaje...')
          }
          rows={1}
          value={value}
        />
        <button
          aria-label={isSubmitting ? 'Enviando mensaje' : 'Enviar mensaje'}
          className="grid size-11 shrink-0 cursor-pointer place-items-center rounded-lg border-0 bg-blue-700 text-white transition-colors hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:cursor-not-allowed disabled:bg-slate-300"
          disabled={!canSubmit}
          type="submit"
        >
          <SendIcon />
        </button>
      </form>
      <p className="mx-auto mt-2 mb-0 max-w-3xl text-center text-xs text-slate-400">
        Enter para enviar · Shift + Enter para una nueva línea
      </p>
    </div>
  )
}
