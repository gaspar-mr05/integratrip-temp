import type { InputHTMLAttributes } from 'react'

type TextInputProps = InputHTMLAttributes<HTMLInputElement> & {
  inputClassName?: string
  label: string
}

export function TextInput({
  id,
  inputClassName = '',
  label,
  className = '',
  ...props
}: TextInputProps) {
  const inputId = id ?? props.name

  return (
    <label className={`grid gap-1.5 ${className}`.trim()} htmlFor={inputId}>
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className={`min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 shadow-none outline-none transition-colors placeholder:text-slate-400 hover:border-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 ${inputClassName}`.trim()}
        id={inputId}
        {...props}
      />
    </label>
  )
}
