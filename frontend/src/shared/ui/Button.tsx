import type { ButtonHTMLAttributes } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary'
}

export function Button({
  className = '',
  type = 'button',
  variant = 'primary',
  ...props
}: ButtonProps) {
  const variantClassName =
    variant === 'primary'
      ? 'border-blue-700 bg-blue-700 text-white hover:border-blue-800 hover:bg-blue-800'
      : 'border-slate-300 bg-white text-slate-800 hover:border-slate-400 hover:bg-slate-50'

  return (
    <button
      className={`min-h-10 cursor-pointer rounded-md border px-4 text-sm font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:cursor-not-allowed disabled:opacity-50 ${variantClassName} ${className}`.trim()}
      type={type}
      {...props}
    />
  )
}
