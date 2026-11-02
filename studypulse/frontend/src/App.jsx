import { useEffect, useState } from "react";
import {
  getSessions,
  createSession,
  updateSession,
  deleteSession,
  getTip,
} from "./services/api";

function App() {
  const [sessions, setSessions] = useState([]);
  const [subject, setSubject] = useState("");
  const [minutes, setMinutes] = useState("");
  const [tip, setTip] = useState("");
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

  const handleSubmit = async (e) => {
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

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this session?")) return;
    await deleteSession(id);
    load();
  };

  const handleTip = async () => {
    setTip("Thinking...");
    try {
      const res = await getTip(lang);
      console.log("TIP RESPONSE:", res.data);
      setTip(res.data.tip || "No tip came back. Try again.");
    } catch (err) {
      console.error(err);
      setTip("Could not get a tip. Check the backend.");
    }
  };

  const gap = { marginLeft: 8 };

  return (
    <div style={{ maxWidth: 520, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>StudyPulse</h1>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="Minutes"
          value={minutes}
          onChange={(e) => setMinutes(e.target.value)}
          required
        />
        <button type="submit">Add</button>
      </form>

      <ul>
        {sessions.map((s) => (
          <li key={s.id} style={{ marginBottom: 8 }}>
            {editingId === s.id ? (
              <>
                <input
                  value={editSubject}
                  onChange={(e) => setEditSubject(e.target.value)}
                />
                <input
                  type="number"
                  value={editMinutes}
                  onChange={(e) => setEditMinutes(e.target.value)}
                />
                <button style={gap} onClick={() => saveEdit(s)}>Save</button>
                <button style={gap} onClick={() => setEditingId(null)}>Cancel</button>
              </>
            ) : (
              <>
                {s.subject} - {s.minutes} min
                {s.created_at && ` (${new Date(s.created_at).toLocaleDateString()})`}
                <button style={gap} onClick={() => startEdit(s)}>Edit</button>
                <button style={gap} onClick={() => handleDelete(s.id)}>Delete</button>
              </>
            )}
          </li>
        ))}
      </ul>

      <select value={lang} onChange={(e) => setLang(e.target.value)}>
        <option value="en">English</option>
        <option value="km">ខ្មែរ</option>
      </select>
      <button onClick={handleTip}>Get study tip</button>
      {tip && <p>{tip}</p>}
    </div>
  );
}

export default App;