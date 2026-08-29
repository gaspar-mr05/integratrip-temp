export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL as string

export async function requestJson<TResponse>(
  path: string,
  init?: RequestInit,
): Promise<TResponse> {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    credentials: 'include',
    ...init,
    headers: {
      ...init?.headers,
    },
  })

  if (!response.ok) {
    throw new ApiError('Request failed', response.status)
  }

  return response.json() as Promise<TResponse>
}
