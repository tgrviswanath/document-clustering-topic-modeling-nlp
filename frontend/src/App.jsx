import React, { useState } from "react";
import { Container, Box, Tabs, Tab } from "@mui/material";
import Header from "./components/Header";
import TopicModelingPage from "./pages/TopicModelingPage";
import ClusteringPage from "./pages/ClusteringPage";

export default function App() {
  const [tab, setTab] = useState(0);
  return (
    <>
      <Header />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
          <Tab label="Topic Modeling (LDA / NMF)" />
          <Tab label="Document Clustering (KMeans)" />
        </Tabs>
        <Box>{tab === 0 ? <TopicModelingPage /> : <ClusteringPage />}</Box>
      </Container>
    </>
  );
}
