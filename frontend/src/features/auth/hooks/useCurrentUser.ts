import { useCurrentUserContext } from '../providers/authContext'

export function useCurrentUser() {
  return useCurrentUserContext()
}
