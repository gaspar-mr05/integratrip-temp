import { login, logout } from '../../features/auth/api'
import type { CurrentUser } from '../../features/auth/types'
import { Button } from '../../shared/ui'

type NavbarProps = {
  isLoadingUser: boolean
  user: CurrentUser | null
}

export function Navbar({ isLoadingUser, user }: NavbarProps) {
  const isAuthenticated = user !== null

  return (
    <header className="flex min-h-16 items-center justify-between gap-4 border-b border-slate-200 bg-white px-8">
      <a className="text-base font-bold text-slate-950 no-underline" href="/">
        MCP Client
      </a>

      <nav className="flex items-center gap-3" aria-label="Principal">
        {isLoadingUser ? (
          <span className="max-w-72 truncate text-sm text-slate-600">
            Cargando...
          </span>
        ) : isAuthenticated ? (
          <>
            <span className="max-w-72 truncate text-sm text-slate-600">
              {user.user_id}
            </span>
            <Button onClick={logout} variant="secondary">
              Logout
            </Button>
          </>
        ) : (
          <Button onClick={login}>Login</Button>
        )}
      </nav>
    </header>
  )
}
