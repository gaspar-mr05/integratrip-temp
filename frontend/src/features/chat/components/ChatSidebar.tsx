import { ErrorMessage } from '../../../shared/ui'
import type { ConversationSummary } from '../types'
import { ConversationList } from './ConversationList'
import { PlusIcon } from './icons'

type ChatSidebarProps = {
  activeConversationId: string | null
  conversations: readonly ConversationSummary[]
  error: Error | null
  isCreating: boolean
  isLoading: boolean
  onCreateConversation: () => Promise<void>
  onSelectConversation: (conversationId: string) => void
}

export function ChatSidebar({
  activeConversationId,
  conversations,
  error,
  isCreating,
  isLoading,
  onCreateConversation,
  onSelectConversation,
}: ChatSidebarProps) {
  return (
    <aside className="flex min-h-0 flex-col border-r border-slate-200 bg-[#f1f1ee] p-3 sm:p-4">
      <button
        className="flex min-h-11 cursor-pointer items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-900 transition-colors hover:border-slate-400 hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:cursor-not-allowed disabled:opacity-60 sm:justify-start"
        disabled={isCreating}
        onClick={() => void onCreateConversation()}
        type="button"
      >
        <PlusIcon />
        <span className="sr-only sm:not-sr-only">
          {isCreating ? 'Creando...' : 'Nuevo chat'}
        </span>
      </button>

      <div className="mt-7 min-h-0 flex-1 overflow-y-auto">
        <p className="mb-2 hidden px-2 text-xs font-semibold tracking-[0.12em] text-slate-500 uppercase sm:block">
          Conversaciones
        </p>
        {error ? (
          <div className="mb-3">
            <ErrorMessage message={error.message} />
          </div>
        ) : null}
        <ConversationList
          conversations={conversations}
          isLoading={isLoading}
          activeConversationId={activeConversationId}
          onSelectConversation={onSelectConversation}
        />
      </div>
    </aside>
  )
}
