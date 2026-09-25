import { useRef, useState } from 'react'

import {
  ActiveConversationPanel,
  ChatHeader,
  ChatSidebar,
  MessageComposer,
} from '../components'
import { useActiveConversation, useConversations } from '../hooks'

export function ChatPage() {
  const [messageDraft, setMessageDraft] = useState('')
  const selectedConversationIdRef = useRef<string | null>(null)
  const {
    conversations,
    createConversation,
    error: conversationsError,
    isCreating,
    isLoading: areConversationsLoading,
    updateConversationSummary,
  } = useConversations()
  const {
    activeConversation,
    activeConversationId,
    approveConfirmation,
    error: activeConversationError,
    isLoading: isActiveConversationLoading,
    isSending,
    pendingUserMessage,
    processingConfirmationId,
    rejectConfirmation,
    selectConversation,
    sendMessage,
  } = useActiveConversation({
    onConversationUpdated: updateConversationSummary,
  })
  const hasPendingConfirmations =
    (activeConversation?.pending_confirmations.length ?? 0) > 0

  async function handleCreateConversation(): Promise<void> {
    const createdConversation = await createConversation()

    if (createdConversation) {
      setMessageDraft('')
      selectedConversationIdRef.current = createdConversation.id
      selectConversation(createdConversation.id)
    }
  }

  function handleSelectConversation(conversationId: string): void {
    if (conversationId !== activeConversationId) {
      setMessageDraft('')
    }

    selectedConversationIdRef.current = conversationId
    selectConversation(conversationId)
  }

  async function handleSendMessage(): Promise<void> {
    const message = messageDraft.trim()

    if (!message) {
      return
    }

    const sendingConversationId = activeConversationId
    const sendRequest = sendMessage(message)
    setMessageDraft('')
    const wasSent = await sendRequest

    if (
      !wasSent &&
      selectedConversationIdRef.current === sendingConversationId
    ) {
      setMessageDraft((currentDraft) => currentDraft || message)
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
        onSelectConversation={handleSelectConversation}
      />

      <div className="flex min-h-0 min-w-0 flex-col bg-[#f7f7f5]">
        <ChatHeader title={headerTitle} />
        <ActiveConversationPanel
          conversation={activeConversation}
          error={activeConversationError}
          isLoading={isActiveConversationLoading}
          onApproveConfirmation={approveConfirmation}
          onRejectConfirmation={rejectConfirmation}
          pendingUserMessage={pendingUserMessage}
          processingConfirmationId={processingConfirmationId}
        />
        <MessageComposer
          disabled={
            activeConversation === null ||
            isActiveConversationLoading ||
            hasPendingConfirmations
          }
          isSubmitting={isSending}
          onChange={setMessageDraft}
          onSubmit={handleSendMessage}
          placeholder={
            hasPendingConfirmations
              ? 'Resuelve la confirmación pendiente para continuar...'
              : undefined
          }
          value={messageDraft}
        />
      </div>
    </section>
  )
}
