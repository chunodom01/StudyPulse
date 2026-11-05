import { useState } from "react";
import { Link } from "react-router-dom";
import { getQuiz } from "../services/api";

const GRADES = [7, 8, 9, 10, 11, 12];

const SUBJECTS = [
  { value: "Mathematics", label: "Mathematics · គណិតវិទ្យា" },
  { value: "Physics", label: "Physics · រូបវិទ្យា" },
  { value: "Chemistry", label: "Chemistry · គីមីវិទ្យា" },
  { value: "Biology", label: "Biology · ជីវវិទ្យា" },
  { value: "Earth Science", label: "Earth Science · ផែនដីវិទ្យា" },
  { value: "Khmer Language", label: "Khmer Language · ភាសាខ្មែរ" },
  { value: "History", label: "History · ប្រវត្តិវិទ្យា" },
  { value: "Geography", label: "Geography · ភូមិសាស្ត្រ" },
  { value: "Moral & Civics", label: "Moral & Civics · សីលធម៌-ពលរដ្ឋវិជ្ជា" },
  { value: "English", label: "English · ភាសាអង់គ្លេស" },
  { value: "ICT", label: "ICT · ព័ត៌មានវិទ្យា" },
];

export default function Quiz() {
  const [grade, setGrade] = useState(7);
  const [subject, setSubject] = useState("Mathematics");
  const [count, setCount] = useState(5);
  const [lang, setLang] = useState("en");
  const [topic, setTopic] = useState("");

  const [questions, setQuestions] = useState([]);
  const [picked, setPicked] = useState({});
  const [revealed, setRevealed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true);
    setError("");
    setQuestions([]);
    setPicked({});
    setRevealed(false);
    try {
      const res = await getQuiz({ grade, subject, count, lang, topic });
      setQuestions(res.data.questions);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Could not make a quiz. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const pick = (qi, oi) => {
    if (revealed) return;
    setPicked({ ...picked, [qi]: oi });
  };

  const score = questions.filter((q, i) => picked[i] === q.answer_index).length;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">🧠 Quiz</div>
        <div className="topbar-right">
          <Link className="btn btn-ghost" to="/">← Dashboard</Link>
        </div>
      </header>

      <section className="card">
        <h2>Make a quiz</h2>
        <div className="row">
          <label className="field">
            Grade
            <select value={grade} onChange={(e) => setGrade(Number(e.target.value))}>
              {GRADES.map((g) => (
                <option key={g} value={g}>Grade {g}</option>
              ))}
            </select>
          </label>

          <label className="field grow">
            Subject
            <select value={subject} onChange={(e) => setSubject(e.target.value)}>
              {SUBJECTS.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </label>

          <label className="field">
            Questions
            <select value={count} onChange={(e) => setCount(Number(e.target.value))}>
              <option value={5}>5</option>
              <option value={10}>10</option>
            </select>
          </label>

          <label className="field">
            Language
            <select value={lang} onChange={(e) => setLang(e.target.value)}>
              <option value="en">English</option>
              <option value="km">ខ្មែរ</option>
            </select>
          </label>
        </div>

        <div className="row" style={{ marginTop: 10 }}>
          <input
            placeholder="Lesson or topic (optional), e.g. fractions"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            maxLength={100}
          />
          <button className="btn" onClick={generate} disabled={loading}>
            {loading ? "Making quiz..." : questions.length ? "New quiz" : "Start quiz"}
          </button>
        </div>

        {error && <div className="error" style={{ marginTop: 12 }}>{error}</div>}
        <p className="muted" style={{ margin: "12px 0 0", fontSize: "0.85rem" }}>
          Made by AI for practice. Check with your textbook if an answer looks wrong.
        </p>
      </section>

      {questions.length > 0 && (
        <section className="card">
          <h2>Grade {grade} · {subject}</h2>

          {questions.map((q, qi) => (
            <div className="q" key={qi}>
              <div className="q-title">{qi + 1}. {q.question}</div>
              <div className="opts">
                {q.options.map((opt, oi) => {
                  const cls = ["opt"];
                  if (revealed && oi === q.answer_index) cls.push("correct");
                  else if (revealed && picked[qi] === oi) cls.push("wrong");
                  else if (!revealed && picked[qi] === oi) cls.push("selected");
                  return (
                    <button key={oi} className={cls.join(" ")} onClick={() => pick(qi, oi)}>
                      {opt}
                    </button>
                  );
                })}
              </div>
              {revealed && <div className="explain">💡 {q.explanation}</div>}
            </div>
          ))}

          <div className="row" style={{ marginTop: 16 }}>
            {!revealed ? (
              <button className="btn" onClick={() => setRevealed(true)}>Show answers</button>
            ) : (
              <span className="score">Score: {score} / {questions.length}</span>
            )}
          </div>
        </section>
      )}
    </div>
  );
}