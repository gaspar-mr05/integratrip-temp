import type { PropsWithChildren } from 'react'

type PanelProps = PropsWithChildren<{
  title: string
  description?: string
}>

export function Panel({ children, description, title }: PanelProps) {
  return (
    <section className="grid w-full max-w-lg gap-6 rounded-lg border border-slate-200 bg-white p-6">
      <div>
        <h1 className="m-0 text-4xl leading-none font-bold text-slate-950 md:text-6xl">
          {title}
        </h1>
        {description ? (
          <p className="mt-3 mb-0 text-slate-600">{description}</p>
        ) : null}
      </div>
      {children}
    </section>
  )
}
