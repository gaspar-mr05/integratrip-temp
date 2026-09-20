import type { ConversationSummary } from '../types'
import { ChatIcon } from './icons'

const lastActivityFormatter = new Intl.DateTimeFormat('es-CL', {
  dateStyle: 'short',
  timeStyle: 'short',
})

type ConversationListItemProps = {
  conversation: ConversationSummary
  isActive: boolean
  onSelectConversation: (conversationId: string) => void
}

export function ConversationListItem({
  conversation,
  isActive,
  onSelectConversation,
}: ConversationListItemProps) {
  const updatedAt = new Date(conversation.updated_at)
  const lastActivity = Number.isNaN(updatedAt.getTime())
    ? null
    : lastActivityFormatter.format(updatedAt)

  return (
    <button
      aria-label={conversation.title}
      aria-pressed={isActive}
      className={`flex min-h-10 cursor-pointer items-center justify-center gap-2 rounded-md border-0 px-3 text-left text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:justify-start ${isActive ? 'bg-slate-200 text-slate-950' : 'bg-transparent text-slate-600 hover:bg-slate-200/70 hover:text-slate-950'}`}
      onClick={() => onSelectConversation(conversation.id)}
      type="button"
    >
      <span className="shrink-0">
        <ChatIcon />
      </span>
      <span className="hidden min-w-0 sm:block">
        <span className="block truncate">{conversation.title}</span>
        {lastActivity ? (
          <span className="block truncate text-xs text-slate-400">
            {lastActivity}
          </span>
        ) : null}
      </span>
    </button>
  )
}
