// geometry.js – geometry utilities for LiteDoc PDF parser

/**
 * Topological sort using Kahn's algorithm with spatial heuristics.
 * Used to determine the correct reading order of blocks based on their 
 * spatial coordinates (x, y) and bounding boxes.
 */
export function topologicalSort(blocks) {
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

      const axMin = a.xMin ?? (a.bbox && a.bbox.xMin) ?? 0;
      const axMax = a.xMax ?? (a.bbox && a.bbox.xMax) ?? 0;
      const ayMin = a.yMin ?? (a.bbox && a.bbox.yMin) ?? 0;
      const ayMax = a.yMax ?? (a.bbox && a.bbox.yMax) ?? 0;

      const bxMin = b.xMin ?? (b.bbox && b.bbox.xMin) ?? 0;
      const bxMax = b.xMax ?? (b.bbox && b.bbox.xMax) ?? 0;
      const byMin = b.yMin ?? (b.bbox && b.bbox.yMin) ?? 0;
      const byMax = b.yMax ?? (b.bbox && b.bbox.yMax) ?? 0;

      // Vertical ordering constraint:
      // a is above b, and they overlap horizontally
      const vertOverlapAmt = Math.max(0, Math.min(axMax, bxMax) - Math.max(axMin, bxMin));
      const minW = Math.min(axMax - axMin, bxMax - bxMin);
      const vertOverlap = vertOverlapAmt > Math.min(10, minW * 0.1);
      const isAbove = ayMin >= byMax - 10; // tolerance of 10px
      
      // Horizontal ordering constraint:
      // a is to the left of b, and they overlap vertically
      const isLeft = axMax <= bxMin + 20;
      const vertOverlapY = Math.max(ayMin, byMin) < Math.min(ayMax, byMax) + 20;

      if ((isAbove && vertOverlap) || (isLeft && vertOverlapY)) {
        adj[i].push(j);
        inDegree[j]++;
      }
    }
  }

  const queue = [];
  for (let i = 0; i < n; i++) {
    if (inDegree[i] === 0) {
      queue.push(i);
    }
  }

  let result = [];
  while (queue.length > 0) {
    // Custom heuristic: sort queue to prioritize leftmost (xMin) for distinct columns,
    // then topmost (yMax) for blocks within the same column.
    queue.sort((idxA, idxB) => {
      const a = blocks[idxA];
      const b = blocks[idxB];
      
      const axMin = a.xMin ?? (a.bbox && a.bbox.xMin) ?? 0;
      const axMax = a.xMax ?? (a.bbox && a.bbox.xMax) ?? 0;
      const ayMax = a.yMax ?? (a.bbox && a.bbox.yMax) ?? 0;

      const bxMin = b.xMin ?? (b.bbox && b.bbox.xMin) ?? 0;
      const bxMax = b.xMax ?? (b.bbox && b.bbox.xMax) ?? 0;
      const byMax = b.yMax ?? (b.bbox && b.bbox.yMax) ?? 0;

      const horizOverlapAmt = Math.max(0, Math.min(axMax, bxMax) - Math.max(axMin, bxMin));
      const minWidth = Math.min(axMax - axMin, bxMax - bxMin);
      const horizOverlap = horizOverlapAmt > Math.min(15, minWidth * 0.15);
      
      if (!horizOverlap) {
        return axMin - bxMin; // distinct columns: leftmost first
      }

      const yDiff = byMax - ayMax;
      if (Math.abs(yDiff) < 15) {
        return axMin - bxMin; // leftmost first if on same logical row
      }
      return yDiff; // topmost first
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

export function dbscan(points, eps, minPts) {
  const clusters = [];
  const visited = new Set();
  const noise = [];
  function bboxDist(a, b) {
    const aXMin = a.x || a.xMin || 0;
    const aXMax = a.xMax || (aXMin + (a.width || 0));
    const aYMin = a.y || a.yMin || 0;
    const aYMax = a.yMax || (aYMin + (a.height || 0));

    const bXMin = b.x || b.xMin || 0;
    const bXMax = b.xMax || (bXMin + (b.width || 0));
    const bYMin = b.y || b.yMin || 0;
    const bYMax = b.yMax || (bYMin + (b.height || 0));

    const dx = Math.max(0, Math.max(aXMin - bXMax, bXMin - aXMax));
    const dy = Math.max(0, Math.max(aYMin - bYMax, bYMin - aYMax));
    
    const dxPenalty = dx > 0 ? dx * 20 : 0;
    return Math.hypot(dxPenalty, dy);
  }

  function regionQuery(pIdx) {
    const neighbors = [];
    const p = points[pIdx];
    for (let i = 0; i < points.length; i++) {
      if (i === pIdx) continue;
      const q = points[i];
      const dist = bboxDist(p, q);
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

export function inferFontStyle(fontName) {
  const lower = (fontName || '').toLowerCase();
  return {
    isBold: lower.includes('bold'),
    isItalic: lower.includes('italic') || lower.includes('oblique')
  };
}

export function intervalRelation(a, b) {
  if (a.yMax <= b.yMin) return 'before';
  if (b.yMax <= a.yMin) return 'after';
  return 'overlaps';
}

export function orderBlocksAllen(blocks) {
  return blocks.slice().sort((a, b) => {
    const rel = intervalRelation(a, b);
    if (rel === 'before') return 1;
    if (rel === 'after') return -1;
    return a.xMin - b.xMin;
  });
}

export function computeVoronoi(points) {
  return [];
}
