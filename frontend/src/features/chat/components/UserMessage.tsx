type UserMessageProps = {
  text: string
}

export function UserMessage({ text }: UserMessageProps) {
  return (
    <article className="flex justify-end" aria-label="Mensaje del usuario">
      <p className="m-0 max-w-[85%] whitespace-pre-wrap break-words rounded-xl rounded-br-sm bg-blue-700 px-4 py-3 text-sm leading-6 text-white shadow-sm sm:max-w-[75%]">
        {text}
      </p>
    </article>
  )
}
