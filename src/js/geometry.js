// geometry.js – geometry utilities for LiteDoc PDF parser
// Voronoi diagram generation (placeholder implementation)
function computeVoronoi(points) {
  // Simple placeholder: returns empty array of cells.
  // In a full implementation, this would compute the Voronoi diagram of the points.
  return [];
}

// DBSCAN clustering implementation (basic O(n^2) version)
function dbscan(points, eps, minPts) {
  const clusters = [];
  const visited = new Set();
  const noise = [];
  function regionQuery(pIdx) {
    const neighbors = [];
    const p = points[pIdx];
    for (let i = 0; i < points.length; i++) {
      const q = points[i];
      const dist = Math.hypot(p.x - q.x, p.y - q.y);
      if (dist <= eps) neighbors.push(i);
    }
    return neighbors;
  }
  function expandCluster(pIdx, neighbors, clusterIdx) {
    clusters[clusterIdx].push(pIdx);
    for (let i = 0; i < neighbors.length; i++) {
      const qIdx = neighbors[i];
      if (!visited.has(qIdx)) {
        visited.add(qIdx);
        const qNeighbors = regionQuery(qIdx);
        if (qNeighbors.length >= minPts) {
          neighbors = neighbors.concat(qNeighbors);
        }
      }
      // add to cluster if not already assigned
      let already = false;
      for (const c of clusters) {
        if (c.includes(qIdx)) { already = true; break; }
      }
      if (!already) {
        clusters[clusterIdx].push(qIdx);
      }
    }
  }
  for (let i = 0; i < points.length; i++) {
    if (visited.has(i)) continue;
    visited.add(i);
    const neighbors = regionQuery(i);
    if (neighbors.length < minPts) {
      noise.push(i);
    } else {
      const cluster = [];
      clusters.push(cluster);
      expandCluster(i, neighbors, clusters.length - 1);
    }
  }
  return { clusters, noise };
}

// Font‑style heuristics: infer bold/italic from font name
function inferFontStyle(fontName) {
  const lower = (fontName || '').toLowerCase();
  return {
    isBold: lower.includes('bold'),
    isItalic: lower.includes('italic') || lower.includes('oblique')
  };
}

// Allen's interval algebra for vertical intervals (y axis)
function intervalRelation(a, b) {
  if (a.yMax <= b.yMin) return 'before';
  if (b.yMax <= a.yMin) return 'after';
  return 'overlaps';
}

// Order blocks using interval relation, then horizontal position
// PDF coords: y increases upward.  Reading order: top → bottom (descending y).
function orderBlocksAllen(blocks) {
  return blocks.slice().sort((a, b) => {
    const rel = intervalRelation(a, b);
    // 'before' means a is below b on the page → a comes AFTER b
    if (rel === 'before') return 1;
    // 'after' means a is above b on the page → a comes BEFORE b
    if (rel === 'after') return -1;
    // Overlap: sort by left coordinate (left-to-right)
    return a.xMin - b.xMin;
  });
}

// Topological sort using Kahn's algorithm with spatial heuristics
function topologicalSort(blocks) {
  const n = blocks.length;
  if (n === 0) return [];
  const inDegree = new Array(n).fill(0);
  const adj = Array.from({ length: n }, () => []);

  // Build the graph using vertical and horizontal rules
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i === j) continue;
      const a = blocks[i];
      const b = blocks[j];

      // Vertical ordering constraint:
      // a is above b, and they overlap horizontally
      const vertOverlap = Math.max(a.xMin, b.xMin) < Math.min(a.xMax, b.xMax);
      const isAbove = a.yMin >= b.yMax - 5; // tolerance of 5px
      
      // Horizontal ordering constraint:
      // a is to the left of b, and they overlap vertically
      const horizOverlap = a.xMax <= b.xMin + 5;
      const vertOverlapY = Math.max(a.yMin, b.yMin) < Math.min(a.yMax, b.yMax);

      if ((isAbove && vertOverlap) || (horizOverlap && vertOverlapY)) {
        adj[i].push(j);
        inDegree[j]++;
      }
    }
  }

  // Find all nodes with in-degree 0
  const queue = [];
  for (let i = 0; i < n; i++) {
    if (inDegree[i] === 0) {
      queue.push(i);
    }
  }

  const result = [];
  while (queue.length > 0) {
    // Custom heuristic: sort queue to prioritize leftmost (xMin), then topmost (yMax)
    queue.sort((idxA, idxB) => {
      const a = blocks[idxA];
      const b = blocks[idxB];
      if (Math.abs(a.xMin - b.xMin) > 8) {
        return a.xMin - b.xMin; // leftmost first
      }
      return b.yMax - a.yMax; // topmost first (descending Y)
    });

    const u = queue.shift();
    result.push(blocks[u]);

    for (const v of adj[u]) {
      inDegree[v]--;
      if (inDegree[v] === 0) {
        queue.push(v);
      }
    }
  }

  // Fallback: if there was a cycle, add remaining blocks in default layout order
  if (result.length < n) {
    const seen = new Set(result);
    for (const b of blocks) {
      if (!seen.has(b)) {
        result.push(b);
      }
    }
  }

  return result;
}

// Export to global window for use in pdf-parser.js
window.computeVoronoi = computeVoronoi;
window.dbscan = dbscan;
window.inferFontStyle = inferFontStyle;
window.intervalRelation = intervalRelation;
window.orderBlocksAllen = orderBlocksAllen;
window.topologicalSort = topologicalSort;
