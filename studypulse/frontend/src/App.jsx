import { useEffect, useState } from "react";
import { getSessions, createSession, getTip } from "./services/api";

function App() {
  const [sessions, setSessions] = useState([]);
  const [subject, setSubject] = useState("");
  const [minutes, setMinutes] = useState("");
  const [tip, setTip] = useState("");

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

  const handleTip = async () => {
    setTip("Thinking...");
    const res = await getTip();
    setTip(res.data.tip);
  };

  return (
    <div style={{ maxWidth: 480, margin: "40px auto", fontFamily: "sans-serif" }}>
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
          <li key={s.id}>
            {s.subject} - {s.minutes} min
            {s.created_at && ` (${new Date(s.created_at).toLocaleDateString()})`}
          </li>
        ))}
      </ul>

      <button onClick={handleTip}>Get study tip</button>
      {tip && <p>{tip}</p>}
    </div>
  );
}

export default App;