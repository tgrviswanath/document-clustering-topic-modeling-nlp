import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import BubbleChartIcon from "@mui/icons-material/BubbleChart";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <BubbleChartIcon sx={{ mr: 1 }} />
        <Typography variant="h6" fontWeight="bold">
          Document Clustering & Topic Modeling
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
