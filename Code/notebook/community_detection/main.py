<!doctype html>
<html lang="it">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Cluster Graph 3D</title>
    <style>
      body { margin: 0; overflow: hidden; background: #d0d0d0; }
      #graph3d { width: 100vw; height: 100vh; display: block; }
      /* Controlli: dropdown clustering */
      #controls {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 10;
        background: #ffffff;
        padding: 8px 12px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        font-family: sans-serif;
      }
      #info-panel {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 400px;
        max-height: 85vh;
        overflow-y: auto;
        padding: 16px;
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        display: none;
        z-index: 10;
      }
      #info-close {
        position: absolute;
        top: 8px;
        right: 8px;
        border: none;
        background: transparent;
        font-size: 20px;
        cursor: pointer;
      }
      #top-users-list { list-style: none; margin: 0; padding: 0; }
      .user-card { margin-bottom: 12px; padding: 8px; background: #fafafa;
                   border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
      .user-card summary {
        font-size: 1.05em;
        font-weight: bold;
        cursor: pointer;
        margin-bottom: 6px;
        list-style: none;
      }
      .user-card dl {
        display: grid;
        grid-template-columns: max-content 1fr;
        column-gap: 8px;
        row-gap: 4px;
        font-size: 0.9em;
      }
      .user-card dt { color: #555; }
      .user-card dd { margin: 0; color: #222; }
    </style>
  </head>
  <body>
    <!-- Dropdown per selezione metodo di clustering -->
    <div id="controls">
      <label for="cluster-method">Metodo di clustering:&nbsp;</label>
      <select id="cluster-method">
        <option value="louvain">Louvain</option>
        <option value="label_propagation">Label Propagation</option>
        <option value="girvan_newman">Girvan-Newman</option>
        <option value="walktrap">Walktrap</option>
        <option value="leiden">Leiden</option>
        <option value="dbscan">DBSCAN</option>
        <option value="kmeans">K-Means</option>
        <option value="fcm">FCM</option>
        <option value="gaussian_mixture">Gaussian Mixture</option>
        <option value="affinity_propagation">Affinity Propagation</option>
        <option value="modularity_maximization">Modularity Maximization</option>
      </select>
    </div>

    <div id="graph3d"></div>
    <div id="info-panel">
      <button id="info-close">×</button>
      <h3 id="info-title"></h3>
      <ul id="top-users-list"></ul>
    </div>

    <!-- Librerie esterne -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/3d-force-graph"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>

    <script>
      (function() {
        // Mappa metodo -> file JSON
        const fileMap = {
          'louvain': 'louvain_cluster_stats.json',
          'label_propagation': 'label_propagation_cluster_stats.json',
          'girvan_newman': 'girvan_newman_cluster_stats.json',
          'walktrap': 'walktrap_cluster_stats.json',
          'leiden': 'leiden_cluster_stats.json',
          'dbscan': 'dbscan_cluster_stats.json',
          'kmeans': 'kmeans_cluster_stats.json',
          'fcm': 'fcm_cluster_stats.json',
          'gaussian_mixture': 'gaussian_mixture_cluster_stats.json',
          'affinity_propagation': 'affinity_propagation_cluster_stats.json',
          'modularity_maximization': 'modularity_maximization_cluster_stats.json'
        };

        const selectEl = document.getElementById('cluster-method');
        const panel    = document.getElementById('info-panel');
        const titleEl  = document.getElementById('info-title');
        const listEl   = document.getElementById('top-users-list');
        const closeBtn = document.getElementById('info-close');

        let Graph3D;
        let clusterStats;

        // Carica e visualizza i dati del cluster selezionato
        async function loadCluster(method) {
          const url = fileMap[method];
          try {
            const res = await fetch(url);
            if (!res.ok) throw new Error(res.statusText);
            clusterStats = await res.json();
          } catch(err) {
            console.error('Errore caricamento JSON:', err);
            return;
          }

          // Prepara nodi e link
          const counts   = Object.values(clusterStats).map(s => s.num_nodes);
          const minCount = Math.min(...counts);
          const maxCount = Math.max(...counts);
          const radiusScale = d3.scaleLinear()
            .domain([minCount, maxCount])
            .range([12, 35]);
          const colorScale  = d3.scaleOrdinal(d3.schemeCategory10);

          const nodes = Object.entries(clusterStats).map(([id, stats]) => ({
            id,
            cluster: +id,
            count: stats.num_nodes
          }));

          const links = [];
          Object.entries(clusterStats).forEach(([id, stats]) => {
            if (Array.isArray(stats.connected_clusters)) {
              stats.connected_clusters.forEach(target => {
                if (+id < +target) links.push({ source: id, target: String(target) });
              });
            }
          });

          const graphData = { nodes, links };

          // Inizializza o aggiorna il grafico
          if (!Graph3D) {
            Graph3D = ForceGraph3D()(document.getElementById('graph3d'))
              .backgroundColor('#e0e0e0')
              .enableNavigationControls(true)
              .linkColor(() => 'rgba(100,100,100,0.6)')
              .linkOpacity(0.6)
              .linkWidth(1)
              .nodeColor(d => colorScale(d.cluster))
              .nodeThreeObject(d =>
                new THREE.Mesh(
                  new THREE.SphereGeometry(radiusScale(d.count)),
                  new THREE.MeshPhongMaterial({ color: colorScale(d.cluster) })
                )
              )
              .nodeLabel(d => `Cluster ${d.cluster}\nUtenti: ${d.count}`)
              .onNodeClick(node => showInfo(node));

            // Forze
            Graph3D.d3Force('charge').strength(-50);
            Graph3D.d3Force('link')
              .distance(() => 400)
              .strength(0.5);
          }

          // Aggiorna i dati nel grafico e reset info
          Graph3D.graphData(graphData);
          panel.style.display = 'none';
        }

        // Mostra pannello informazioni su nodo
        function showInfo(node) {
          const stats = clusterStats[node.id];
          titleEl.innerHTML = `
            <strong>Cluster ${node.cluster}</strong><br>
            <ul style="list-style: none; padding-left: 0;">
              <li><strong>num_nodes:</strong> ${stats.num_nodes}</li>
              <li><strong>num_edges:</strong> ${stats.num_edges}</li>
              <li><strong>avg_degree:</strong> ${stats.avg_degree.toFixed(2)}</li>
              <li><strong>density:</strong> ${stats.density.toFixed(4)}</li>
              <li><strong>num_communities:</strong> ${stats.num_communities}</li>
              <li><strong>modularity:</strong> ${stats.modularity.toFixed(4)}</li>
              <li><strong>coverage:</strong> ${stats.coverage.toFixed(4)}</li>
              <li><strong>performance:</strong> ${stats.performance.toFixed(4)}</li>
            </ul>
            <hr>
            <strong>Top utenti</strong>
          `;

          listEl.innerHTML = '';
          if (Array.isArray(stats.top_users) && stats.top_users.length) {
            stats.top_users.forEach(u => {
              const li = document.createElement('li');
              li.innerHTML = `
                <details class="user-card">
                  <summary><strong>${u.username || u.user_pk}</strong> (grado: ${u.degree})</summary>
                  <dl>
                    <dt>User PK:</dt><dd>${u.user_pk}</dd>
                    <dt>Post count:</dt><dd>${u.post_count}</dd>
                    <dt>Total likes:</dt><dd>${u.total_likes}</dd>
                    <dt>Avg likes:</dt><dd>${u.avg_likes.toFixed(2)}</dd>
                    <dt>Total quotes:</dt><dd>${u.total_quotes}</dd>
                    <dt>Total reposts:</dt><dd>${u.total_reposts}</dd>
                    <dt>Total reshares:</dt><dd>${u.total_reshares}</dd>
                    <dt>Avg sentiment:</dt><dd>${u.avg_sentiment.toFixed(3)}</dd>
                    <dt>First post:</dt><dd>${u.first_post || "N/A"}</dd>
                    <dt>Last post:</dt><dd>${u.last_post || "N/A"}</dd>
                  </dl>
                </details>
              `;
              listEl.appendChild(li);
            });
          } else {
            listEl.innerHTML = '<li><em>Nessun dato disponibile</em></li>';
          }

          panel.style.display = 'block';
        }

        // Chiudi pannello info
        closeBtn.addEventListener('click', () => panel.style.display = 'none');

        // Cambia cluster al cambio selezione
        selectEl.addEventListener('change', () => loadCluster(selectEl.value));

        // Caricamento iniziale
        loadCluster(selectEl.value);
      })();
    </script>
  </body>
</html>