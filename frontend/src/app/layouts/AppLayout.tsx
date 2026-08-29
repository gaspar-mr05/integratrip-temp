import type { PropsWithChildren } from 'react'

import { useCurrentUser } from '../../features/auth/hooks'
import { Navbar } from './Navbar'

export function AppLayout({ children }: PropsWithChildren) {
  const { isLoading, user } = useCurrentUser()

  return (
    <div className="grid min-h-svh grid-rows-[auto_1fr] bg-[#f7f7f5] text-slate-950 antialiased">
      <Navbar isLoadingUser={isLoading} user={user} />
      <main className="px-5 py-10 sm:px-8 sm:py-14 lg:px-12">{children}</main>
    </div>
  )
}
