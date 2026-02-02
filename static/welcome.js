document.addEventListener('DOMContentLoaded', () => {
  const $chat = document.getElementById('chat');
  const $q    = document.getElementById('q');
  const $send = document.getElementById('send');
  const $dbBtn = document.getElementById('db-btn');
  const $graphContainer = document.getElementById('graph-container');

  let messages = [];
  let fullGraphData = null;
  let graphVisible = false;

  const converter = new showdown.Converter();
  const esc = (s) => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  // Helper to add chat bubbles
  const bubble = (role, text) => {
    const b = document.createElement('div');
    b.className = `bubble ${role === 'user' ? 'user' : 'bot'}`;
    b.innerHTML = converter.makeHtml(text);
    $chat.appendChild(b);
    $chat.scrollTop = $chat.scrollHeight;
    return b;
  };

  const plainText = (text, className) => {
    const p = document.createElement('div');
    p.className = className;
    p.textContent = text;
    $chat.appendChild(p);
    $chat.scrollTop = $chat.scrollHeight;
    return p;
  };

  // Toggle Graph View
  $dbBtn.addEventListener('click', () => {
    graphVisible = !graphVisible;
    $dbBtn.classList.toggle('active', graphVisible);

    // Toggle display
    $chat.style.display = graphVisible ? 'none' : 'flex';
    $graphContainer.style.display = graphVisible ? 'block' : 'none';

    if (graphVisible) {
      $q.placeholder = 'Explore the graph structure above.';
      renderGraph();
    } else {
      $q.placeholder = 'Ask a question about the graph...';
    }
  });

  // Send Message
  async function send() {
    const text = ($q.value || '').trim();
    if (!text) return;

    $q.value = '';
    // messages array is no longer used for request history
    bubble('user', esc(text));

    const loadingText = plainText('Thinking...', 'loading-text');

    try {
      const res = await fetch('/api/chat', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ query: text })
      });
      const raw = await res.text();
      let data; try { data = JSON.parse(raw); } catch { data = { reply: raw }; }

      loadingText.classList.add('fade-out');
      setTimeout(() => loadingText.remove(), 500);

      if (!res.ok) {
        bubble('bot', `Error: ${esc(data.error || 'Server error')}`);
        return;
      }

      const reply = data.reply || '(no reply)';
      bubble('bot', reply);

    } catch (e) {
      loadingText.remove();
      console.error(e);
      bubble('bot', 'Request failed. Check console.');
    }
  }

  $send.addEventListener('click', send);
  $q.addEventListener('keydown', (e)=>{ if(e.key==='Enter') send(); });

  // Tooltip Logic
  const $tip = document.getElementById('kg-tooltip');

  function showTip(html, x, y) {
    $tip.innerHTML = html;
    $tip.style.display = 'block';
    // Positioning logic
    const rect = $tip.getBoundingClientRect();
    let tx = x + 15, ty = y + 15;
    if (tx + rect.width > window.innerWidth) tx = x - rect.width - 15;
    if (ty + rect.height > window.innerHeight) ty = y - rect.height - 15;
    $tip.style.left = tx + 'px';
    $tip.style.top  = ty + 'px';
  }
  function hideTip() { $tip.style.display = 'none'; }

  function getTooltipContent(d) {
    let lines = [`<div style="font-weight:bold; margin-bottom:4px;">${esc(d.id)}</div>`];
    for (const [k, v] of Object.entries(d)) {
      if (['id', 'x', 'y', 'fx', 'fy', 'index', 'vx', 'vy'].includes(k)) continue;
      lines.push(`<div><b>${esc(k)}:</b> ${esc(v)}</div>`);
    }
    return lines.join('');
  }

  // Graph Rendering with D3
  async function renderGraph() {
    if (!fullGraphData) {
      try {
        const res = await fetch('/api/knowledge-graph');
        if (!res.ok) throw new Error('Failed to load graph');
        fullGraphData = await res.json();
      } catch (e) {
        console.error(e);
        return;
      }
    }

    const width = $graphContainer.offsetWidth;
    const height = 600;

    const svg = d3.select("#knowledge-graph");
    svg.selectAll("*").remove(); // Clear previous

    svg.attr("width", width).attr("height", height);

    // Zoom support
    const g = svg.append("g");
    const zoom = d3.zoom().scaleExtent([0.1, 4]).on("zoom", (e) => {
      g.attr("transform", e.transform);
    });
    svg.call(zoom);

    const nodes = (fullGraphData.nodes || []).map(d => ({...d}));
    const links = (fullGraphData.links || fullGraphData.edges || []).map(d => ({...d}));

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide(20));

    // Draw lines (edges)
    const link = g.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5)
      .on("mouseover", (e, d) => {
        showTip(`<b>Relation:</b> ${esc(d.type || 'linked')}<br><b>Source:</b> ${d.source.id}<br><b>Target:</b> ${d.target.id}`, e.clientX, e.clientY);
      })
      .on("mouseout", hideTip);

    // Draw circles (nodes)
    const node = g.append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 10)
      .attr("fill", d => {
          // Simple color logic based on label or random
          const colors = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6"];
          if(d.label) {
             let hash = 0;
             for (let i = 0; i < d.label.length; i++) hash = d.label.charCodeAt(i) + ((hash << 5) - hash);
             return colors[Math.abs(hash) % colors.length];
          }
          return "#2563eb";
      })
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .call(d3.drag()
        .on("start", (e, d) => {
          if (!e.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on("end", (e, d) => {
          if (!e.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      )
      .on("mouseover", (e, d) => showTip(getTooltipContent(d), e.clientX, e.clientY))
      .on("mouseout", hideTip);

    // Draw labels
    const label = g.append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text(d => d.id)
      .attr("x", 12)
      .attr("y", 3)
      .attr("font-size", "12px")
      .attr("fill", "#333")
      .style("pointer-events", "none");

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      label
        .attr("x", d => d.x + 12)
        .attr("y", d => d.y + 3);
    });
  }

  // Initial greeting
  bubble("bot", "Hello! I am your GraphRAG assistant. Ask me anything about the knowledge graph.");
});
