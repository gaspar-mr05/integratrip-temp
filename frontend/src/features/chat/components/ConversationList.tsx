import { Skeleton } from '../../../shared/ui'
import type { ConversationSummary } from '../types'
import { ConversationListItem } from './ConversationListItem'

type ConversationListProps = {
  conversations: readonly ConversationSummary[]
  isLoading: boolean
  activeConversationId: string | null
  onSelectConversation: (conversationId: string) => void
}

export function ConversationList({
  conversations,
  isLoading,
  activeConversationId,
  onSelectConversation,
}: ConversationListProps) {
  if (isLoading) {
    return (
      <div aria-label="Cargando conversaciones" className="grid gap-2">
        <Skeleton className="h-10" />
        <Skeleton className="h-10" />
        <Skeleton className="h-10" />
      </div>
    )
  }

  if (conversations.length === 0) {
    return (
      <p className="m-0 px-2 text-sm leading-6 text-slate-500">
        No hay conversaciones.
      </p>
    )
  }

  return (
    <nav aria-label="Conversaciones" className="grid gap-1">
      {conversations.map((conversation) => (
        <ConversationListItem
          conversation={conversation}
          isActive={conversation.id === activeConversationId}
          key={conversation.id}
          onSelectConversation={onSelectConversation}
        />
      ))}
    </nav>
  )
}
