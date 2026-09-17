type ChatHeaderProps = {
  title: string
}

export function ChatHeader({ title }: ChatHeaderProps) {
  return (
    <div className="border-b border-slate-200/80 px-5 py-4 sm:px-8">
      <p className="m-0 truncate text-sm font-semibold text-slate-900">
        {title}
      </p>
    </div>
  )
}
