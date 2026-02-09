import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import * as d3 from "d3";

function useCarbonSummary(userId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetch(`/api/carbon/summary/${userId}`);
      if (resp.ok) {
        const json = await resp.json();
        setData(json);
      }
    } catch (e) {
      console.error("Failed to load carbon summary", e);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return { data, loading, refetch: fetchSummary };
}

function createMockHistory(totalSessions, totalCo2, totalTrees) {
  if (!totalSessions) return [];
  const sessions = Math.min(totalSessions, 8);
  const avgCo2 = totalCo2 / sessions || 0;
  const avgTrees = totalTrees / sessions || 0;
  return Array.from({ length: sessions }).map((_, i) => ({
    index: i + 1,
    co2_kg: Math.max(0, avgCo2 + (Math.random() - 0.5) * 0.4 * avgCo2),
    trees: Math.max(0, avgTrees + (Math.random() - 0.5) * 0.5 * avgTrees),
  }));
}

function ImpactChart({ data }) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !data || !data.length) return;
    el.innerHTML = "";

    const width = el.clientWidth || 700;
    const height = 240;
    const margin = { top: 10, right: 30, bottom: 30, left: 40 };

    const svg = d3
      .select(el)
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    const x = d3
      .scaleBand()
      .domain(data.map((d) => d.index))
      .range([margin.left, width - margin.right])
      .padding(0.3);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.co2_kg) * 1.2])
      .nice()
      .range([height - margin.bottom, margin.top]);

    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).tickSizeOuter(0));

    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    svg
      .selectAll("rect")
      .data(data)
      .enter()
      .append("rect")
      .attr("x", (d) => x(d.index))
      .attr("y", (d) => y(d.co2_kg))
      .attr("width", x.bandwidth())
      .attr("height", (d) => y(0) - y(d.co2_kg))
      .attr("rx", 6)
      .attr("fill", "#22c55e");
  }, [data]);

  return <div id="chart" ref={ref} />;
}

export function App() {
  const [userId] = useState(1);
  const [topic, setTopic] = useState("écologie numérique");
  const [level, setLevel] = useState("beginner");
  const [duration, setDuration] = useState(30);
  const [lastContent, setLastContent] = useState(null);
  const { data, loading, refetch } = useCarbonSummary(userId);

  const historyData = useMemo(
    () =>
      data
        ? createMockHistory(
            data.total_sessions,
            data.total_co2_kg,
            data.total_trees_to_fund
          )
        : [],
    [data]
  );

  const handleGenerate = async () => {
    try {
      const resp = await fetch("/api/learning/path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          topic,
          level,
          duration_minutes: Number(duration),
        }),
      });
      if (resp.ok) {
        const json = await resp.json();
        setLastContent(json);
        refetch();
      } else {
        alert("Erreur lors de la génération du parcours");
      }
    } catch (e) {
      console.error(e);
      alert("Impossible de joindre l'API backend");
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1>EcoLearn AI</h1>
        <p>Apprentissage personnalisé + impact carbone mesuré en temps réel.</p>
      </header>
      <main className="main">
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Impact carbone de votre apprentissage</h2>
              <span className="badge">MVP Demo</span>
            </div>
            <small>User ID: {userId}</small>
          </div>

          <div className="form-row">
            <input
              type="text"
              placeholder="Sujet (climat, énergie...)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              <option value="beginner">Débutant</option>
              <option value="intermediate">Intermédiaire</option>
              <option value="advanced">Avancé</option>
            </select>
            <input
              type="number"
              min={5}
              max={240}
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            />
            <button onClick={handleGenerate}>Générer un parcours</button>
          </div>

          <div className="metrics">
            <div className="metric">
              <div className="metric-label">Sessions totales</div>
              <div className="metric-value">
                {data ? data.total_sessions : loading ? "..." : "0"}
              </div>
            </div>
            <div className="metric">
              <div className="metric-label">CO₂ généré</div>
              <div className="metric-value">
                {data
                  ? `${data.total_co2_kg.toFixed(2)} kg`
                  : loading
                  ? "..."
                  : "0 kg"}
              </div>
            </div>
            <div className="metric">
              <div className="metric-label">Arbres à financer</div>
              <div className="metric-value">
                {data
                  ? data.total_trees_to_fund.toFixed(2)
                  : loading
                  ? "..."
                  : "0.00"}
              </div>
            </div>
          </div>

          {historyData.length > 0 && <ImpactChart data={historyData} />}

          {lastContent && (
            <div className="content">
              <h3>{lastContent.content.title}</h3>
              <p>{lastContent.content.summary}</p>
              <ol>
                {lastContent.content.steps.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ol>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

