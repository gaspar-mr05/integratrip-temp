import { ErrorMessage, Skeleton } from '../../../shared/ui'
import {
  ChatEmptyState,
  ChatHeader,
  ChatSidebar,
  ConversationMessages,
  MessageComposer,
} from '../components'
import { useActiveConversation, useConversations } from '../hooks'

export function ChatPage() {
  const {
    conversations,
    createConversation,
    error: conversationsError,
    isCreating,
    isLoading: areConversationsLoading,
  } = useConversations()
  const {
    activeConversation,
    activeConversationId,
    error: activeConversationError,
    isLoading: isActiveConversationLoading,
    selectConversation,
  } = useActiveConversation()

  async function handleCreateConversation(): Promise<void> {
    const createdConversation = await createConversation()

    if (createdConversation) {
      selectConversation(createdConversation.id)
    }
  }

  const headerTitle = isActiveConversationLoading
    ? 'Cargando conversación...'
    : (activeConversation?.conversation.title ?? 'Nueva conversación')

  return (
    <section
      aria-label="Chat"
      className="grid h-full min-h-0 grid-cols-[4.75rem_minmax(0,1fr)] bg-white sm:grid-cols-[17rem_minmax(0,1fr)]"
    >
      <ChatSidebar
        activeConversationId={activeConversationId}
        conversations={conversations}
        error={conversationsError}
        isCreating={isCreating}
        isLoading={areConversationsLoading}
        onCreateConversation={handleCreateConversation}
        onSelectConversation={selectConversation}
      />

      <div className="flex min-h-0 min-w-0 flex-col bg-[#f7f7f5]">
        <ChatHeader title={headerTitle} />
        {activeConversationError ? (
          <div className="grid min-h-0 flex-1 place-items-center px-5 py-10 sm:px-8">
            <ErrorMessage message={activeConversationError.message} />
          </div>
        ) : isActiveConversationLoading ? (
          <div
            aria-label="Cargando conversación"
            className="mx-auto grid w-full max-w-3xl flex-1 content-center gap-4 px-5 py-10 sm:px-8"
          >
            <Skeleton className="h-20" />
            <Skeleton className="h-28" />
          </div>
        ) : activeConversation && activeConversation.messages.length > 0 ? (
          <ConversationMessages messages={activeConversation.messages} />
        ) : (
          <ChatEmptyState />
        )}
        <MessageComposer />
      </div>
    </section>
  )
}
