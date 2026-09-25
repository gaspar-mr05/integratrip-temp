export function normalizeError(
  currentError: unknown,
  fallbackMessage: string,
): Error {
  return currentError instanceof Error
    ? currentError
    : new Error(fallbackMessage)
}
