import React, { useState } from "react";
import {
  Box, TextField, Button, CircularProgress, Alert, Typography,
  Paper, Chip, Slider, Table, TableBody, TableCell, TableHead, TableRow,
} from "@mui/material";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { runCluster } from "../services/clusterApi";

const COLORS = ["#1976d2", "#388e3c", "#f57c00", "#7b1fa2", "#c62828", "#00838f", "#558b2f"];

const SAMPLE_TEXTS = [
  "The stock market rallied as investors reacted to strong earnings reports from major tech companies.",
  "Federal Reserve officials signaled a pause in interest rate hikes amid cooling inflation data.",
  "Apple unveiled its latest iPhone model featuring advanced AI capabilities and improved battery life.",
  "Scientists discovered a new exoplanet in the habitable zone of a nearby star system.",
  "The Premier League title race intensified as Manchester City and Arsenal drew in a thrilling match.",
  "NASA's Artemis mission successfully completed a lunar orbit test ahead of crewed moon landing.",
  "Google announced major updates to its search algorithm incorporating large language models.",
  "The World Health Organization issued new guidelines on antibiotic resistance prevention.",
  "Electric vehicle sales surged globally as battery costs continued to decline in 2024.",
  "A new study links regular exercise to significantly reduced risk of cardiovascular disease.",
  "The US economy added 250,000 jobs in March, beating analyst expectations by a wide margin.",
  "Researchers developed a biodegradable plastic alternative made from seaweed extract.",
  "The Champions League semi-finals produced dramatic results with two comeback victories.",
  "Microsoft integrated GPT-4 into its Office suite, transforming document creation workflows.",
  "Climate scientists warned that Arctic ice melt is accelerating faster than previous models predicted.",
];

export default function ClusteringPage() {
  const [texts, setTexts] = useState(SAMPLE_TEXTS.join("\n"));
  const [nClusters, setNClusters] = useState(4);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRun = async () => {
    const docs = texts.split("\n").map((t) => t.trim()).filter(Boolean);
    if (docs.length < nClusters) {
      setError(`Need at least ${nClusters} documents for ${nClusters} clusters.`);
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await runCluster(docs, nClusters);
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Request failed.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? result.clusters.map((c) => ({ name: `Cluster ${c.cluster_id}`, docs: c.size }))
    : [];

  return (
    <Box>
      <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap", alignItems: "center" }}>
        <Box sx={{ minWidth: 200 }}>
          <Typography variant="caption">Clusters: {nClusters}</Typography>
          <Slider value={nClusters} min={2} max={10} step={1}
            onChange={(_, v) => setNClusters(v)} size="small" />
        </Box>
        <Button variant="contained" onClick={handleRun} disabled={loading}
          startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}>
          {loading ? "Clustering..." : "Run KMeans"}
        </Button>
      </Box>

      <TextField
        fullWidth multiline rows={6}
        label="Documents (one per line)"
        value={texts}
        onChange={(e) => setTexts(e.target.value)}
        sx={{ mb: 2 }}
        size="small"
      />

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Box>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            KMeans — {result.n_clusters} Clusters
          </Typography>

          {/* Cluster term chips */}
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1.5, mb: 3 }}>
            {result.clusters.map((c) => (
              <Paper key={c.cluster_id} variant="outlined" sx={{ p: 1.5, minWidth: 180 }}>
                <Typography variant="caption" fontWeight="bold"
                  color={COLORS[c.cluster_id % COLORS.length]}>
                  Cluster {c.cluster_id} ({c.size} docs)
                </Typography>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
                  {c.top_terms.map((w) => (
                    <Chip key={w} label={w} size="small"
                      sx={{ bgcolor: COLORS[c.cluster_id % COLORS.length] + "22" }} />
                  ))}
                </Box>
              </Paper>
            ))}
          </Box>

          {/* Cluster size bar chart */}
          <Typography variant="subtitle2" gutterBottom>Documents per Cluster</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="docs" radius={[4, 4, 0, 0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Document assignments */}
          <Typography variant="subtitle2" sx={{ mt: 2 }} gutterBottom>Document Assignments</Typography>
          <Paper variant="outlined" sx={{ maxHeight: 300, overflow: "auto" }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>#</TableCell>
                  <TableCell>Cluster</TableCell>
                  <TableCell>Document (preview)</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {result.doc_assignments.map((d) => {
                  const docText = texts.split("\n").filter(Boolean)[d.doc_index] || "";
                  return (
                    <TableRow key={d.doc_index}>
                      <TableCell>{d.doc_index}</TableCell>
                      <TableCell>
                        <Chip label={`Cluster ${d.cluster_id}`} size="small"
                          sx={{ bgcolor: COLORS[d.cluster_id % COLORS.length] + "33" }} />
                      </TableCell>
                      <TableCell sx={{ maxWidth: 400 }}>
                        <Typography variant="body2" noWrap>{docText}</Typography>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </Paper>
        </Box>
      )}
    </Box>
  );
}
