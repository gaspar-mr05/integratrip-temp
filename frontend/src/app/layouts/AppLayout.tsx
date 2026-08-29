import type { PropsWithChildren } from 'react'

import { useCurrentUser } from '../../features/auth/hooks'
import { Navbar } from './Navbar'

export function AppLayout({ children }: PropsWithChildren) {
  const { isLoading, user } = useCurrentUser()

  return (
    <div className="grid min-h-svh grid-rows-[auto_1fr] bg-slate-50 text-slate-950 antialiased">
      <Navbar isLoadingUser={isLoading} user={user} />
      <main className="p-8">{children}</main>
    </div>
  )
}
