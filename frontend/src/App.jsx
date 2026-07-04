import { useState, useEffect, useCallback } from 'react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function ago(d) {
  if (!d) return 'never'
  const s = Math.floor((Date.now() - new Date(d)) / 1000)
  if (s < 60) return `${s}s ago`
  if (s < 3600) return `${Math.floor(s/60)}m ago`
  return `${Math.floor(s/3600)}h ago`
}

export default function App() {
  const [urls, setUrls]       = useState([])
  const [url, setUrl]         = useState('')
  const [label, setLabel]     = useState('')
  const [adding, setAdding]   = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [err, setErr]         = useState('')

  const load = useCallback(async () => {
    setRefreshing(true)
    try { 
      setUrls(await (await fetch(`${API}/api/urls`)).json()) 
    } catch {}
    finally {
      // Simulate a small delay for visible UI feedback if load is instant
      setTimeout(() => setRefreshing(false), 300)
    }
  }, [])

  useEffect(() => { load(); const t = setInterval(load, 30000); return () => clearInterval(t) }, [load])

  async function add(e) {
    e.preventDefault(); setErr('')
    if (!url.trim()) return setErr('Enter a URL')
    setAdding(true)
    try {
      const r = await fetch(`${API}/api/urls`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim(), label: label.trim() })
      })
      if (r.status === 409) return setErr('Already monitored')
      if (!r.ok) return setErr('Failed to add')
      setUrl(''); setLabel(''); load()
    } catch { setErr('Backend unreachable') }
    finally { setAdding(false) }
  }

  async function del(id) {
    await fetch(`${API}/api/urls/${id}`, { method: 'DELETE' })
    setUrls(p => p.filter(u => u.id !== id))
  }

  const up   = urls.filter(u => u.status === 'up').length
  const down = urls.filter(u => u.status === 'down').length
  const lat  = urls.filter(u => u.response_time != null).map(u => u.response_time)
  const avg  = lat.length ? Math.round(lat.reduce((a,b) => a+b,0)/lat.length) : null

  return (
    <div className="page">
      <div className="header">
        <h1><span>UP</span>time</h1>
        <button className="refresh-btn" onClick={load} disabled={refreshing}>
          ↻ {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="stats">
        <div className="stat total"><label>Total</label><div className="val">{urls.length}</div></div>
        <div className="stat up">   <label>Up</label>   <div className="val">{up}</div></div>
        <div className="stat down"> <label>Down</label>  <div className="val">{down}</div></div>
        <div className="stat ms">   <label>Avg ms</label><div className="val">{avg ?? '—'}</div></div>
      </div>

      <form className="form" onSubmit={add}>
        <input placeholder="https://example.com" value={url}   onChange={e => setUrl(e.target.value)} />
        <input placeholder="Label (optional)"     value={label} onChange={e => setLabel(e.target.value)} style={{maxWidth:140}} />
        <button className="btn" disabled={adding}>{adding ? '…' : '+ Add'}</button>
      </form>
      {err && <div className="err">{err}</div>}

      {urls.length === 0
        ? <div className="empty">No URLs yet. Add one above.</div>
        : <div className="cards">
            {urls.map(u => {
              const s = u.status ?? 'unknown'
              return (
                <div key={u.id} className="card">
                  <div className={`dot ${s}`} />
                  <div className="info">
                    <div className="url">{u.url}</div>
                    {u.label && <div className="lbl">{u.label}</div>}
                  </div>
                  <div className="meta">
                    <span className={`badge ${s}`}>{u.status ?? 'pending'}</span>
                    <span className="sub">{u.response_time != null ? `${u.response_time}ms · ` : ''}{ago(u.last_checked)}</span>
                  </div>
                  <button className="del" onClick={() => del(u.id)}>✕</button>
                </div>
              )
            })}
          </div>
      }
    </div>
  )
}
