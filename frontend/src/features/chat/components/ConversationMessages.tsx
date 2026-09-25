import type { ChatMessage } from '../types'
import { AssistantMessage } from './AssistantMessage'
import { ToolMessage } from './ToolMessage'
import { UserMessage } from './UserMessage'

type ConversationMessagesProps = {
  messages: readonly ChatMessage[]
}

export function ConversationMessages({ messages }: ConversationMessagesProps) {
  return (
    <div className="grid gap-5">
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
          default: {
            const unexpectedRole: never = message.role
            return unexpectedRole
          }
        }
      })}
    </div>
  )
}
