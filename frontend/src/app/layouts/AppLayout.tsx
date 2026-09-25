import type { PropsWithChildren } from 'react'

import { useCurrentUser } from '../../features/auth/hooks'
import { Navbar } from './Navbar'

type AppLayoutProps = PropsWithChildren<{
  fullBleed?: boolean
}>

export function AppLayout({ children, fullBleed = false }: AppLayoutProps) {
  const { isLoading, user } = useCurrentUser()

  return (
    <div
      className={`grid grid-rows-[auto_1fr] bg-[#f7f7f5] text-slate-950 antialiased ${fullBleed ? 'h-svh overflow-hidden' : 'min-h-svh'}`}
    >
      <Navbar isLoadingUser={isLoading} user={user} />
      <main
        className={
          fullBleed
            ? 'min-h-0 overflow-hidden'
            : 'px-5 py-10 sm:px-8 sm:py-14 lg:px-12'
        }
      >
        {children}
      </main>
    </div>
  )
}
