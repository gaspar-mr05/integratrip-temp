import { useEffect, useRef } from 'react'

import { ErrorMessage, Skeleton } from '../../../shared/ui'
import type { ConversationDetail } from '../types'
import { ChatEmptyState } from './ChatEmptyState'
import { ConversationMessages } from './ConversationMessages'
import { PendingConfirmations } from './PendingConfirmations'
import { TypingIndicator } from './TypingIndicator'
import { UserMessage } from './UserMessage'

type ActiveConversationPanelProps = {
  conversation: ConversationDetail | null
  error: Error | null
  isLoading: boolean
  onApproveConfirmation: (confirmationId: string) => void
  onRejectConfirmation: (confirmationId: string) => void
  pendingUserMessage: string | null
  processingConfirmationId: string | null
}

export function ActiveConversationPanel({
  conversation,
  error,
  isLoading,
  onApproveConfirmation,
  onRejectConfirmation,
  pendingUserMessage,
  processingConfirmationId,
}: ActiveConversationPanelProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const messages = conversation?.messages ?? []
  const pendingConfirmations = conversation?.pending_confirmations ?? []

  useEffect(() => {
    const container = containerRef.current

    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, [conversation, pendingUserMessage])

  if (error && conversation === null) {
    return (
      <div className="grid min-h-0 flex-1 place-items-center px-5 py-10 sm:px-8">
        <ErrorMessage message={error.message} />
      </div>
    )
  }

  if (isLoading) {
    return (
      <div
        aria-label="Cargando conversación"
        className="mx-auto grid w-full max-w-3xl flex-1 content-center gap-4 px-5 py-10 sm:px-8"
      >
        <Skeleton className="h-20" />
        <Skeleton className="h-28" />
      </div>
    )
  }

  if (
    conversation === null ||
    (messages.length === 0 &&
      pendingConfirmations.length === 0 &&
      pendingUserMessage === null &&
      error === null)
  ) {
    return <ChatEmptyState />
  }

  return (
    <div
      className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-8"
      ref={containerRef}
    >
      <div className="mx-auto grid w-full max-w-3xl gap-5">
        {error ? <ErrorMessage message={error.message} /> : null}
        {messages.length > 0 ? (
          <ConversationMessages messages={messages} />
        ) : null}
        {pendingUserMessage !== null ? (
          <div className="grid gap-5">
            <UserMessage text={pendingUserMessage} />
            <TypingIndicator />
          </div>
        ) : null}
        <PendingConfirmations
          onApprove={onApproveConfirmation}
          onReject={onRejectConfirmation}
          pendingConfirmations={pendingConfirmations}
          processingConfirmationId={processingConfirmationId}
        />
      </div>
    </div>
  )
}
