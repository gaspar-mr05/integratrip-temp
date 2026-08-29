type FieldHintProps = {
  description?: string
  error?: string
  example: string | null
  id: string
  isRequired: boolean
  onUseExample: (() => void) | null
  expectation: string
}

export function FieldHint({
  description,
  error,
  example,
  expectation,
  id,
  isRequired,
  onUseExample,
}: FieldHintProps) {
  return (
    <div className="grid gap-1" id={id}>
      <p className="m-0 text-xs font-medium text-slate-500">
        {isRequired ? 'Obligatorio. ' : 'Opcional. '}
        {description ?? expectation}
      </p>
      {description ? (
        <p className="m-0 text-xs leading-5 text-slate-500">{expectation}</p>
      ) : null}
      {example ? (
        <div className="flex flex-wrap items-start gap-x-2 gap-y-1 text-xs leading-5 text-slate-500">
          <span>Ejemplo:</span>
          <code className="max-w-full whitespace-pre-wrap break-words rounded bg-slate-100 px-1.5 py-0.5 text-slate-700">
            {example}
          </code>
          {onUseExample ? (
            <button
              className="cursor-pointer font-semibold text-blue-700 underline decoration-blue-300 underline-offset-2 hover:text-blue-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              onClick={onUseExample}
              type="button"
            >
              Usar ejemplo
            </button>
          ) : null}
        </div>
      ) : null}
      {error ? <p className="m-0 text-xs font-medium text-red-700">{error}</p> : null}
    </div>
  )
}
