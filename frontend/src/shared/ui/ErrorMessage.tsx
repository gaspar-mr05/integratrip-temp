type ErrorMessageProps = {
  message: string
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <p
      className="m-0 border-l-2 border-red-500 pl-3 text-sm leading-6 text-red-700"
      role="alert"
    >
      {message}
    </p>
  )
}
