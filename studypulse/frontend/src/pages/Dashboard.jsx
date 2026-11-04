import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  createSession,
  deleteSession,
  getSessions,
  getTip,
  updateSession,
} from "../services/api";

function Stat({ label, value }) {
  return (
    <div className="card stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
    </div>
  );
}

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [subject, setSubject] = useState("");
  const [minutes, setMinutes] = useState("");
  const [tip, setTip] = useState("");
  const [tipLoading, setTipLoading] = useState(false);
  const [lang, setLang] = useState("en");
  const [editingId, setEditingId] = useState(null);
  const [editSubject, setEditSubject] = useState("");
  const [editMinutes, setEditMinutes] = useState("");

  const load = async () => {
    const res = await getSessions();
    setSessions(Array.isArray(res.data) ? res.data : []);
  };

  useEffect(() => {
    load();
  }, []);

  const stats = useMemo(() => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      days.push({
        key: d.toDateString(),
        label: d.toLocaleDateString(undefined, { weekday: "short" }),
        minutes: 0,
      });
    }
    const bySubject = {};
    let count = 0;
    for (const s of sessions) {
      if (!s.created_at) continue;
      const day = days.find((d) => d.key === new Date(s.created_at).toDateString());
      if (!day) continue;
      day.minutes += s.minutes;
      count += 1;
      const key = s.subject.trim().toLowerCase();
      bySubject[key] = (bySubject[key] || 0) + s.minutes;
    }
    const total = days.reduce((sum, d) => sum + d.minutes, 0);
    const top = Object.keys(bySubject).sort((a, b) => bySubject[b] - bySubject[a])[0] || "-";
    const max = Math.max(...days.map((d) => d.minutes), 1);
    return { days, total, today: days[6].minutes, count, top, max };
  }, [sessions]);

  const handleAdd = async (e) => {
    e.preventDefault();
    await createSession({ subject, minutes: Number(minutes) });
    setSubject("");
    setMinutes("");
    load();
  };

  const startEdit = (s) => {
    setEditingId(s.id);
    setEditSubject(s.subject);
    setEditMinutes(String(s.minutes));
  };

  const saveEdit = async (s) => {
    await updateSession(s.id, {
      subject: editSubject,
      minutes: Number(editMinutes),
      notes: s.notes ?? "",
    });
    setEditingId(null);
    load();
  };

  const remove = async (id) => {
    if (!window.confirm("Delete this session?")) return;
    await deleteSession(id);
    load();
  };

  const askTip = async () => {
    setTipLoading(true);
    setTip("");
    try {
      const res = await getTip(lang);
      setTip(res.data.tip || "No tip came back. Try again.");
    } catch {
      setTip("Could not get a tip. Check the backend.");
    } finally {
      setTipLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">📚 StudyPulse</div>
        <div className="topbar-right">
          <span className="hello">Hi, {user.name} 👋</span>
          <button className="btn btn-ghost" onClick={logout}>Log out</button>
        </div>
      </header>

      <section className="grid-stats">
        <Stat label="Today" value={`${stats.today} min`} />
        <Stat label="Last 7 days" value={`${stats.total} min`} />
        <Stat label="Sessions" value={stats.count} />
        <Stat label="Top subject" value={stats.top} />
      </section>

      <section className="grid-main">
        <div className="card">
          <h2>Last 7 days</h2>
          <div className="chart">
            {stats.days.map((d) => (
              <div className="bar-col" key={d.key}>
                <span className="bar-val">{d.minutes || ""}</span>
                <div className="bar-track">
                  <div className="bar" style={{ height: `${(d.minutes / stats.max) * 100}%` }} />
                </div>
                <span className="bar-label">{d.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>✨ AI study coach</h2>
          <div className="row">
            <select value={lang} onChange={(e) => setLang(e.target.value)}>
              <option value="en">English</option>
              <option value="km">ខ្មែរ</option>
            </select>
            <button className="btn" onClick={askTip} disabled={tipLoading}>
              {tipLoading ? "Thinking..." : "Get tip"}
            </button>
          </div>
          {tip && <p className="tip">{tip}</p>}
        </div>
      </section>

      <section className="card">
        <h2>Add a study session</h2>
        <form className="row" onSubmit={handleAdd}>
          <input placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} required />
          <input type="number" min="1" placeholder="Minutes" value={minutes} onChange={(e) => setMinutes(e.target.value)} required />
          <button className="btn" type="submit">Add</button>
        </form>
      </section>

      <section className="card">
        <h2>Recent sessions</h2>
        {sessions.length === 0 && <p className="muted">No sessions yet. Add your first one above 👆</p>}
        <ul className="list">
          {sessions.map((s) => (
            <li className="item" key={s.id}>
              {editingId === s.id ? (
                <div className="row grow">
                  <input value={editSubject} onChange={(e) => setEditSubject(e.target.value)} />
                  <input type="number" value={editMinutes} onChange={(e) => setEditMinutes(e.target.value)} />
                  <button className="btn" onClick={() => saveEdit(s)}>Save</button>
                  <button className="btn btn-ghost" onClick={() => setEditingId(null)}>Cancel</button>
                </div>
              ) : (
                <>
                  <div className="grow">
                    <strong className="cap">{s.subject}</strong>
                    <span className="muted">
                      {" · "}{s.minutes} min
                      {s.created_at && ` · ${new Date(s.created_at).toLocaleDateString()}`}
                    </span>
                  </div>
                  <button className="btn btn-ghost" onClick={() => startEdit(s)}>Edit</button>
                  <button className="btn btn-danger" onClick={() => remove(s.id)}>Delete</button>
                </>
              )}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}