import { create } from 'zustand'
import { queryClient } from '../lib/queryClient'
import { removeChatKeys } from '../utils/layoutStorage'

const TOKEN_KEY = 'transport_token'

export const useAuthStore = create((set) => ({
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  loading: true,
  setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token)
    set({ token, user })
  },
  setUser(user) {
    set({ user })
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    queryClient.clear() // no previous user's cached data survives logout
    removeChatKeys()
    set({ token: null, user: null })
  },
  setLoading(loading) {
    set({ loading })
  },
}))
