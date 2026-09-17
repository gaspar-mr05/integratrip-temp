import type { ChatMessage } from '../types'
import { AssistantMessage } from './AssistantMessage'
import { ToolMessage } from './ToolMessage'
import { UserMessage } from './UserMessage'

type ConversationMessagesProps = {
  messages: readonly ChatMessage[]
}

export function ConversationMessages({ messages }: ConversationMessagesProps) {
  return (
    <div className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-8">
      <div className="mx-auto grid w-full max-w-3xl gap-5">
        {messages.map((message) => {
          switch (message.role) {
            case 'user':
              return <UserMessage key={message.id} text={message.text} />
            case 'model':
              return (
                <AssistantMessage
                  functionCalls={message.function_calls}
                  key={message.id}
                  text={message.text}
                />
              )
            case 'tool':
              return (
                <ToolMessage
                  functionResults={message.function_results}
                  key={message.id}
                />
              )
          }
        })}
      </div>
    </div>
  )
}
