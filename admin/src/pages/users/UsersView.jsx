import { useCallback, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import api from '../../utils/api'
import { clampPage, sameRows } from '../../utils/autoRefreshCore'
import { useAutoRefresh } from '../../hooks/useAutoRefresh'
import PaginationControls from '../../components/PaginationControls'
import Banner from '../../components/Banner'
import ConfirmModal from '../../components/ConfirmModal'
import BackButton from '../../components/BackButton'
import { Avatar, Badge, Card, DataTable, EmptyState, ErrorState, PageHeader, StatCard } from '../../components/ui'
import { formatISTDate } from '../../utils/formatDate'
import { statusTone } from '../../utils/status'
import { notifyCountsChanged } from '../../utils/events'
import { useAdminAuth } from '../../context/AdminAuthContext'
import EditUserModal from './EditUserModal'
import RowMenu from './RowMenu'
import SelectedUserPanel from './SelectedUserPanel'
import SkeletonRows from './SkeletonRows'
import UsersTabs from './UsersTabs'

const ADMIN_LOCK_TIP = 'Admins can only be changed by themselves.'
const PAGE_SIZE = 30
const ROW_KEYS = ['status', 'role', 'username', 'email', 'updatedAt', 'documentCount']
const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : '')

const icon = (d) => (
  <svg className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">{d}</svg>
)
const ICONS = {
  total: icon(<><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M18 14.5a6.5 6.5 0 0 1 3.5 5.5" /></>),
}

export default function UsersView() {
  const { user: me } = useAdminAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const urlQ = searchParams.get('q') || ''
  const rawRole = searchParams.get('role') || ''
  const role = (rawRole === 'user' || rawRole === 'admin') ? rawRole : ''

  const [users, setUsers] = useState([])
  const [totalPages, setTotalPages] = useState(1)
  const [totalUsers, setTotalUsers] = useState(0)
  const [requestCount, setRequestCount] = useState(0)
  const [counts, setCounts] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [editingUser, setEditingUser] = useState(null)
  const [deletingUser, setDeletingUser] = useState(null)
  const [busyId, setBusyId] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  // Only the newest request may update the table (overlapping loads from fast filter changes).
  const latestRequest = useRef(0)

  // Search box: local text, debounced into the URL `q` param; an external change of `q`
  // (the top-bar search) flows back into the box.
  const [qInput, setQInput] = useState(urlQ)
  const lastWritten = useRef(urlQ)

  const updateParams = useCallback((patch) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      Object.entries(patch).forEach(([k, v]) => (v ? next.set(k, v) : next.delete(k)))
      return next
    }, { replace: true })
  }, [setSearchParams])

  useEffect(() => {
    if (urlQ !== lastWritten.current) {
      lastWritten.current = urlQ
      setQInput(urlQ) // external URL change (top-bar search) -> update the box
    }
  }, [urlQ])

  useEffect(() => {
    const t = setTimeout(() => {
      const term = qInput.trim()
      if (term === lastWritten.current) return
      lastWritten.current = term
      updateParams({ q: term })
    }, 300)
    return () => clearTimeout(t)
  }, [qInput, updateParams])

  // Page resets to 1 whenever a filter changes (derived, no effect).
  const filterKey = `${urlQ}|${role}`
  const [pageState, setPageState] = useState({ key: filterKey, page: 1 })
  const page = pageState.key === filterKey ? pageState.page : 1
  const setPage = useCallback((p) => setPageState({ key: filterKey, page: p }), [filterKey])

  const listParams = useCallback((pageToLoad) => {
    const params = { page: pageToLoad, limit: PAGE_SIZE }
    if (urlQ) params.q = urlQ
    if (role) params.role = role
    return params
  }, [urlQ, role])

  const applyList = useCallback((data) => {
    setUsers((prev) => (sameRows(prev, data.users || [], ROW_KEYS) ? prev : data.users || []))
    setRequestCount(data.passwordRequestCount || 0)
    if (data.statusCounts) setCounts(data.statusCounts)
    setTotalPages(data.totalPages || 1)
    setTotalUsers(data.totalUsers || 0)
  }, [])

  // Quiet refresh on the shell heartbeat: keeps page, filters, search, selection and open menus.
  const { markChanged, noteLoad } = useAutoRefresh({
    fetchData: async () => (await api.get('/admin/users', { params: listParams(page) })).data,
    applyData: (data) => {
      if (page > (data.totalPages || 1)) setPage(clampPage(page, data.totalPages || 1))
      else applyList(data)
    },
    busy: loading || Boolean(busyId),
    modalOpen: Boolean(editingUser || deletingUser),
  })

  const load = useCallback(async (pageToLoad = page) => {
    const requestId = ++latestRequest.current
    noteLoad()
    setLoading(true)
    setLoadError('')
    try {
      const res = await api.get('/admin/users', { params: listParams(pageToLoad) })
      if (requestId !== latestRequest.current) return
      applyList(res.data)
    } catch (err) {
      if (requestId !== latestRequest.current) return
      setLoadError(err.userMessage || 'Could not load users.')
    } finally {
      if (requestId === latestRequest.current) setLoading(false)
    }
  }, [page, listParams, applyList, noteLoad])

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { load() }, [load])

  // Selected user: the list row is the source of truth; GET /admin/users/{id} adds
  // documentCount + lastActiveAt and is fetched only once a row is selected.
  const selected = users.find((u) => u.id === selectedId) || null
  const [detail, setDetail] = useState({ id: null, user: null })
  useEffect(() => {
    if (!selectedId) return undefined
    let off = false
    api.get(`/admin/users/${selectedId}`)
      .then((res) => { if (!off) setDetail({ id: selectedId, user: res.data.user }) })
      .catch(() => { if (!off) setDetail({ id: selectedId, user: null }) })
    return () => { off = true }
  }, [selectedId])
  const detailLoading = Boolean(selectedId) && detail.id !== selectedId

  const mergeUser = (updated) => setUsers((prev) => prev.map((u) => (u.id === updated.id ? { ...u, ...updated } : u)))

  async function toggleRole(user) {
    if (busyId) return
    const nextRole = user.role === 'admin' ? 'user' : 'admin'
    markChanged()
    setBusyId(user.id)
    setError('')
    setSuccess('')
    try {
      const res = await api.patch(`/admin/users/${user.id}`, { role: nextRole })
      mergeUser(res.data.user)
      setSuccess(`${user.username} is now ${nextRole}.`)
    } catch (err) {
      setError(err.userMessage || 'Could not change role.')
    } finally {
      setBusyId(null)
    }
  }

  async function deleteUser(user) {
    if (busyId) return
    markChanged()
    setBusyId(user.id)
    setError('')
    setSuccess('')
    try {
      await api.delete(`/admin/users/${user.id}`)
      setSuccess('User deleted.')
      setDeletingUser(null)
      if (selectedId === user.id) setSelectedId(null)
      notifyCountsChanged()
      load(page)
    } catch (err) {
      setError(err.userMessage || 'Could not delete user.')
      setDeletingUser(null)
    } finally {
      setBusyId(null)
    }
  }

  const stat = (key) => (counts ? counts[key] : '-')
  const hasFilters = Boolean(urlQ || role)
  const from = totalUsers === 0 ? 0 : (page - 1) * PAGE_SIZE + 1
  const to = (page - 1) * PAGE_SIZE + users.length
  const firstLoad = loading && users.length === 0

  function rowActions(u) {
    const busy = busyId === u.id
    // another admin's row: the backend refuses these too (403) - this only greys them out
    const locked = u.role === 'admin' && u.id !== me?.id
    const tip = locked ? ADMIN_LOCK_TIP : undefined
    return (
      <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
        <RowMenu
          label={`More actions for ${u.username}`}
          items={[
            { key: 'view', label: 'View activity', to: `/users/${u.id}` },
            { key: 'edit', label: 'Edit', disabled: locked, title: tip, onClick: () => setEditingUser(u) },
            { key: 'role', label: u.role === 'admin' ? 'Make user' : 'Make admin', disabled: busy || locked, title: tip, onClick: () => toggleRole(u) },
            { key: 'delete', label: 'Delete', danger: true, disabled: busy || locked, title: tip, onClick: () => setDeletingUser(u) },
          ]}
        />
      </div>
    )
  }

  return (
    <main className="mx-auto max-w-[1560px] px-4 py-6 sm:px-6 lg:px-8">
      <BackButton fallback="/" />
      <PageHeader
        title="Users"
        subtitle="Manage accounts and access permissions"
      />

      <UsersTabs active="users" requests={requestCount} />

      <div className="mb-6 grid grid-cols-2 gap-4 @min-[760px]:grid-cols-4">
          <StatCard label="Total users" value={stat('total')} tone="violet" icon={ICONS.total} loading={!counts && loading} to="/users" />
      </div>

      <Banner error={error} success={success} />

      <div className="grid items-start gap-6 @min-[1000px]:grid-cols-[minmax(0,1fr)_340px]">
        <Card className="min-w-0 p-5" aria-label="User directory">
          <div className="mb-4 flex items-baseline gap-3">
            <h2 className="text-[20px] font-bold text-white">User directory</h2>
            {!firstLoad && !loadError && <span className="text-[14px] text-[var(--muted)]">{totalUsers} user{totalUsers !== 1 ? 's' : ''}</span>}
          </div>

          <div className="mb-4 flex flex-wrap items-center gap-3">
            <div className="relative min-w-[200px] flex-1 sm:max-w-[320px]">
              <svg className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-[var(--muted)]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" strokeLinecap="round" /></svg>
              <input
                type="search"
                value={qInput}
                maxLength={100}
                onChange={(e) => setQInput(e.target.value)}
                placeholder="Search by name or email"
                aria-label="Search users by name or email"
                className="input pl-10"
              />
            </div>
                <select
                  value={role}
                  onChange={(e) => updateParams({ role: e.target.value })}
                  aria-label="Filter by role"
                  className="input !w-auto"
                >
                  <option value="">All roles</option>
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
          </div>

          {loadError ? (
            <ErrorState message={loadError} onRetry={() => load(page)} />
          ) : !firstLoad && users.length === 0 ? (
            <EmptyState
              title="No users found"
              hint={hasFilters ? 'Try a different search or filter.' : undefined}
            />
          ) : (
            <div className={loading && !firstLoad ? 'opacity-60 transition-opacity' : undefined} aria-busy={loading}>
              <DataTable minWidth={880}>
                <thead>
                  <tr>
                    <th scope="col">User</th>
                    <th scope="col">Role</th>
                    <th scope="col">Joined</th>
                    <th scope="col">Documents</th>
                    <th scope="col">Status</th>
                    <th scope="col" className="text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {firstLoad ? <SkeletonRows cols={6} /> : users.map((u) => (
                    <tr key={u.id} aria-selected={u.id === selectedId} onClick={() => setSelectedId(u.id)} className="cursor-pointer">
                      <td className="max-w-[240px]">
                        <button type="button" onClick={() => setSelectedId(u.id)} className="flex w-full min-w-0 items-center gap-3 text-left" aria-label={`Select ${u.username}`}>
                          <Avatar id={u.id} name={u.username} size={40} />
                          <span className="min-w-0">
                            <span className="block truncate font-semibold text-white" title={u.username}>{u.username}</span>
                            <span className="block truncate text-[13px] text-[var(--muted)]" title={u.email}>{u.email}</span>
                          </span>
                        </button>
                      </td>
                      <td><Badge tone={u.role === 'admin' ? 'violet' : 'neutral'}>{cap(u.role)}</Badge></td>
                      <td className="whitespace-nowrap text-[var(--muted)]">{formatISTDate(u.createdAt)}</td>
                      <td className="text-white">{u.documentCount ?? '-'}</td>
                      <td><Badge tone={statusTone(u.status)} dot>{cap(u.status)}</Badge></td>
                      <td>{rowActions(u)}</td>
                    </tr>
                  ))}
                </tbody>
              </DataTable>
            </div>
          )}

          {!loadError && users.length > 0 && (
            <p className="mt-4 text-[14px] text-[var(--muted)]">Showing {from}-{to} of {totalUsers} user{totalUsers !== 1 ? 's' : ''}</p>
          )}
          <PaginationControls page={page} totalPages={totalPages} onChange={setPage} />
        </Card>

        <div className={`${selected ? '' : 'hidden @min-[1000px]:block'} @min-[1000px]:sticky @min-[1000px]:top-20`}>
          <SelectedUserPanel
            user={selected}
            detail={detail.id === selectedId ? detail.user : null}
            detailLoading={detailLoading}
          />
        </div>
      </div>

      <AnimatePresence>
        {editingUser && (
          <EditUserModal
            user={editingUser}
            onClose={() => setEditingUser(null)}
            onWrite={markChanged}
            onSaved={(updated, message) => {
              mergeUser(updated)
              setEditingUser(null)
              setSuccess(message)
            }}
          />
        )}
        {deletingUser && (
          <ConfirmModal
            title="Delete this user?"
            message={`Delete ${deletingUser.username} (${deletingUser.email})? This permanently removes their documents, workbooks, and exports. This cannot be undone.`}
            onConfirm={() => deleteUser(deletingUser)}
            onClose={() => setDeletingUser(null)}
            busy={busyId === deletingUser.id}
            strong
          />
        )}
      </AnimatePresence>
    </main>
  )
}
