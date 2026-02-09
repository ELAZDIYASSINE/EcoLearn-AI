(() => {
  const e = React.createElement;

  function useCarbonSummary(userId) {
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(false);

    const fetchSummary = React.useCallback(async () => {
      setLoading(true);
      try {
        const resp = await fetch(`http://localhost:8000/carbon/summary/${userId}`);
        if (resp.ok) {
          const json = await resp.json();
          setData(json);
        }
      } catch (err) {
        console.error("Failed to load carbon summary", err);
      } finally {
        setLoading(false);
      }
    }, [userId]);

    React.useEffect(() => {
      fetchSummary();
    }, [fetchSummary]);

    return { data, loading, refetch: fetchSummary };
  }

  function createMockHistory(totalSessions, totalCo2, totalTrees) {
    if (!totalSessions) return [];
    const sessions = Math.min(totalSessions, 8);
    const avgCo2 = totalCo2 / sessions;
    const avgTrees = totalTrees / sessions;
    return Array.from({ length: sessions }).map((_, i) => ({
      index: i + 1,
      co2_kg: Math.max(0, avgCo2 + (Math.random() - 0.5) * 0.4 * avgCo2),
      trees: Math.max(0, avgTrees + (Math.random() - 0.5) * 0.5 * avgTrees),
    }));
  }

  function ImpactChart({ data }) {
    const ref = React.useRef(null);

    React.useEffect(() => {
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

    return e("div", { id: "chart", ref });
  }

  function App() {
    const [userId, setUserId] = React.useState(1);
    const [topic, setTopic] = React.useState("écologie numérique");
    const [level, setLevel] = React.useState("beginner");
    const [duration, setDuration] = React.useState(30);
    const [lastContent, setLastContent] = React.useState(null);
    const { data, loading, refetch } = useCarbonSummary(userId);

    const handleGenerate = async () => {
      try {
        const resp = await fetch("http://localhost:8000/learning/path", {
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
      } catch (err) {
        console.error(err);
        alert("Impossible de joindre l'API backend");
      }
    };

    const historyData = data
      ? createMockHistory(data.total_sessions, data.total_co2_kg, data.total_trees_to_fund)
      : [];

    return e(
      "div",
      { className: "card" },
      e(
        "div",
        { style: { display: "flex", justifyContent: "space-between", alignItems: "center" } },
        e("div", null, e("h2", null, "Impact carbone de votre apprentissage"), e("span", { className: "badge" }, "MVP Demo")),
        e("small", null, "User ID: ", userId)
      ),
      e(
        "div",
        { className: "form-row" },
        e("input", {
          type: "text",
          placeholder: "Sujet (climat, énergie...)",
          value: topic,
          onChange: (ev) => setTopic(ev.target.value),
        }),
        e(
          "select",
          { value: level, onChange: (ev) => setLevel(ev.target.value) },
          e("option", { value: "beginner" }, "Débutant"),
          e("option", { value: "intermediate" }, "Intermédiaire"),
          e("option", { value: "advanced" }, "Avancé")
        ),
        e("input", {
          type: "number",
          min: 5,
          max: 240,
          value: duration,
          onChange: (ev) => setDuration(ev.target.value),
        }),
        e(
          "button",
          { onClick: handleGenerate },
          "Générer un parcours"
        )
      ),
      e(
        "div",
        { className: "metrics" },
        e(
          "div",
          { className: "metric" },
          e("div", { className: "metric-label" }, "Sessions totales"),
          e("div", { className: "metric-value" }, data ? data.total_sessions : loading ? "..." : "0")
        ),
        e(
          "div",
          { className: "metric" },
          e("div", { className: "metric-label" }, "CO₂ généré"),
          e(
            "div",
            { className: "metric-value" },
            data ? data.total_co2_kg.toFixed(2) + " kg" : loading ? "..." : "0 kg"
          )
        ),
        e(
          "div",
          { className: "metric" },
          e("div", { className: "metric-label" }, "Arbres à financer"),
          e(
            "div",
            { className: "metric-value" },
            data ? data.total_trees_to_fund.toFixed(2) : loading ? "..." : "0.00"
          )
        )
      ),
      historyData.length ? e(ImpactChart, { data: historyData }) : null,
      lastContent &&
        e(
          "div",
          { style: { marginTop: "1.5rem" } },
          e("h3", null, lastContent.content.title),
          e("p", null, lastContent.content.summary),
          e(
            "ol",
            null,
            lastContent.content.steps.map((s, idx) => e("li", { key: idx }, s))
          )
        )
    );
  }

  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(e(App));
})();

