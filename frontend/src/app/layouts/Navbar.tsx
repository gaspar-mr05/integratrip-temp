import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { login, logout } from '../../features/auth/api'
import { clearCurrentUserCache } from '../../features/auth/authCache'
import type { CurrentUser } from '../../features/auth/types'
import { clearMcpCache } from '../../features/mcp/mcpCache'
import { Button } from '../../shared/ui'

type NavbarProps = {
  isLoadingUser: boolean
  user: CurrentUser | null
}

export function Navbar({ isLoadingUser, user }: NavbarProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const isAuthenticated = user !== null

  function handleLogout(): void {
    clearCurrentUserCache()
    clearMcpCache()
    logout()
  }

  return (
    <header className="border-b border-slate-200/80 bg-[#f7f7f5] px-5 sm:px-8 lg:px-12">
      <div className="mx-auto flex min-h-18 max-w-7xl items-center justify-between gap-4">
        <Link className="group inline-flex items-center gap-2.5 text-base font-semibold tracking-tight text-slate-950 no-underline" to="/">
          <span className="grid size-7 place-items-center rounded-sm bg-slate-950 text-xs font-bold tracking-tight text-white transition-transform duration-200 group-hover:-rotate-3">
            GMR
          </span>
          MagnaTrip
        </Link>

        <nav className="relative flex items-center gap-2 sm:gap-3" aria-label="Principal">
          {isLoadingUser ? (
            <>
              <span
                className="size-10 animate-pulse rounded-md border border-slate-200 bg-slate-200 sm:hidden"
                aria-label="Cargando navegación"
              />
              <div className="hidden items-center gap-3 sm:flex" aria-label="Cargando sesión">
                <span className="h-3 w-28 animate-pulse rounded-full bg-slate-200" />
                <span className="h-9 w-20 animate-pulse rounded-md bg-slate-200" />
              </div>
            </>
          ) : isAuthenticated ? (
            <>
              <div className="hidden items-center gap-2 sm:flex sm:gap-3">
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
                <Button onClick={handleLogout} variant="secondary">
                  Logout
                </Button>
              </div>

              <button
                className="grid size-10 place-items-center rounded-md border border-slate-300 bg-white text-slate-950 transition-colors hover:border-slate-400 hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:hidden"
                type="button"
                aria-expanded={isMenuOpen}
                aria-label={isMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
                onClick={() => setIsMenuOpen((current) => !current)}
              >
                <span className="grid w-4 gap-1" aria-hidden="true">
                  <span className="h-0.5 rounded-full bg-slate-950" />
                  <span className="h-0.5 rounded-full bg-slate-950" />
                  <span className="h-0.5 rounded-full bg-slate-950" />
                </span>
              </button>

              {isMenuOpen ? (
                <div className="absolute top-full right-0 z-20 mt-2 grid min-w-44 gap-1 rounded-md border border-slate-200 bg-white p-2 shadow-lg sm:hidden">
                  <NavLink
                    className={({ isActive }) =>
                      [
                        'rounded-md px-3 py-2 text-sm font-medium no-underline transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600',
                        isActive
                          ? 'bg-slate-950 text-white'
                          : 'text-slate-700 hover:bg-slate-100 hover:text-slate-950',
                      ].join(' ')
                    }
                    onClick={() => setIsMenuOpen(false)}
                    to="/mcp"
                  >
                    MCP
                  </NavLink>
                  <button
                    className="cursor-pointer rounded-md border-0 bg-transparent px-3 py-2 text-left text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-950 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                    onClick={handleLogout}
                    type="button"
                  >
                    Logout
                  </button>
                </div>
              ) : null}
            </>
          ) : (
            <Button onClick={login}>Login</Button>
          )}
        </nav>
      </div>
    </header>
  )
}
