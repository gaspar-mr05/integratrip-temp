import { login, logout } from '../../features/auth/api'
import type { CurrentUser } from '../../features/auth/types'
import { Button } from '../../shared/ui'
import { Link, NavLink } from 'react-router-dom'

type NavbarProps = {
  isLoadingUser: boolean
  user: CurrentUser | null
}

export function Navbar({ isLoadingUser, user }: NavbarProps) {
  const isAuthenticated = user !== null

  return (
    <header className="flex min-h-16 items-center justify-between gap-4 border-b border-slate-200 bg-white px-8">
      <Link className="text-base font-bold text-slate-950 no-underline" to="/">
        IntegraTrip
      </Link>

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
            <NavLink
              className={({ isActive }) =>
                [
                  'rounded-md px-4 py-2 text-sm font-semibold no-underline transition',
                  isActive
                    ? 'bg-slate-950 text-white'
                    : 'bg-slate-100 text-slate-950 hover:bg-slate-200',
                ].join(' ')
              }
              to="/mcp"
            >
              MCP
            </NavLink>
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
