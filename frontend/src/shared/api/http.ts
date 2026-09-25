export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string

function isErrorPayload(value: unknown): value is { detail: string } {
  return (
    typeof value === 'object' &&
    value !== null &&
    'detail' in value &&
    typeof value.detail === 'string'
  )
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const payload: unknown = await response.json()
    return isErrorPayload(payload)
      ? payload.detail
      : `Error HTTP ${response.status}: la API no entregó detalles del error`
  } catch {
    return `Error HTTP ${response.status}: la API no entregó una respuesta JSON válida`
  }
}

export async function requestJson<TResponse>(
  path: string,
  init?: RequestInit,
): Promise<TResponse> {
  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      credentials: 'include',
      ...init,
      headers: {
        ...init?.headers,
      },
    })
  } catch {
    throw new ApiError(
      'Error de red: no se pudo conectar con la API. Verifica que el backend esté disponible',
      0,
    )
  }

  if (!response.ok) {
    throw new ApiError(await errorMessage(response), response.status)
  }

  return response.json() as Promise<TResponse>
}
