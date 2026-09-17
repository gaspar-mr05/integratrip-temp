import type { ConversationSummary } from '../types'
import { ChatIcon } from './icons'


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
  return (
    <button
      aria-label={conversation.title}
      aria-pressed={isActive}
      className={`flex min-h-10 cursor-pointer items-center justify-center gap-2 rounded-md border-0 px-3 text-left text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:justify-start ${isActive ? 'bg-slate-200 text-slate-950' : 'bg-transparent text-slate-600 hover:bg-slate-200/70 hover:text-slate-950'}`}
      onClick={() => onSelectConversation(conversation.id)}
      type="button"
    >
      <ChatIcon />
      <span className="hidden truncate sm:block">{conversation.title}</span>
    </button>
  )
}
