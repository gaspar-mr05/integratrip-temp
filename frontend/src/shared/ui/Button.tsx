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
      ? 'border-transparent bg-blue-600 text-white hover:bg-blue-700'
      : 'border-slate-300 bg-white text-slate-950 hover:bg-slate-50'

  return (
    <button
      className={`min-h-10 cursor-pointer rounded-md border px-4 font-semibold transition-colors ${variantClassName} ${className}`.trim()}
      type={type}
      {...props}
    />
  )
}
