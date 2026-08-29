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
    <header className="border-b border-slate-200/80 bg-[#f7f7f5] px-5 sm:px-8 lg:px-12">
      <div className="mx-auto flex min-h-18 max-w-7xl items-center justify-between gap-4">
        <Link className="group inline-flex items-center gap-2.5 text-base font-semibold tracking-tight text-slate-950 no-underline" to="/">
          <span className="grid size-7 place-items-center rounded-sm bg-slate-950 text-xs font-bold tracking-tight text-white transition-transform duration-200 group-hover:-rotate-3">
            GMR
          </span>
          MagnaTrip
        </Link>

        <nav className="flex items-center gap-2 sm:gap-3" aria-label="Principal">
          {isLoadingUser ? (
            <div className="hidden items-center gap-3 sm:flex" aria-label="Cargando sesión">
              <span className="h-3 w-28 animate-pulse rounded-full bg-slate-200" />
              <span className="h-9 w-20 animate-pulse rounded-md bg-slate-200" />
            </div>
          ) : isAuthenticated ? (
            <>
              <span className="hidden max-w-52 truncate text-sm text-slate-500 md:block">
                {user.user_id}
              </span>
              <NavLink
                className={({ isActive }) =>
                  [
                    'rounded-md px-3 py-2 text-sm font-medium no-underline transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600',
                    isActive
                      ? 'bg-slate-950 text-white'
                      : 'text-slate-600 hover:bg-slate-200/70 hover:text-slate-950',
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
      </div>
    </header>
  )
}
