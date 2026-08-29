import type { InputHTMLAttributes } from 'react'

type TextInputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string
}

export function TextInput({ id, label, className = '', ...props }: TextInputProps) {
  const inputId = id ?? props.name

  return (
    <label className={`grid gap-1.5 ${className}`.trim()} htmlFor={inputId}>
      <span className="text-sm font-semibold text-slate-700">{label}</span>
      <input
        className="min-h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
        id={inputId}
        {...props}
      />
    </label>
  )
}
