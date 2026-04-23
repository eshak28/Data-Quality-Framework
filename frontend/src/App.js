import React, { useState } from "react";
import {
  Container, Typography, Card, CardContent, Grid, Button, TextField, LinearProgress
} from "@mui/material";
import { BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from "recharts";
import { useDropzone } from "react-dropzone";
import { motion } from "framer-motion";

// 🎨 THEME
const primary = "#f472b6";
const secondary = "#e0e7ff";
const textDark = "#1e293b";
const colors = [primary, secondary, "#22c55e", "#f59e0b"];

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);

  const [chat, setChat] = useState([]);
  const [query, setQuery] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  // ✅ FIXED UPLOAD
  const onDrop = async (acceptedFiles) => {
    try {
      const f = acceptedFiles[0];
      setFile(f);

      const formData = new FormData();
      formData.append("file", f);

      const res = await fetch("http://127.0.0.1:8001/api/upload", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();

      // 🔥 FIX
      setResult(data);

    } catch (err) {
      console.error(err);
      alert("❌ Upload failed. Check backend.");
    }
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  // CHAT
  const sendQuery = async () => {
    if (!query) return;

    setChatLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8001/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: query,
          data: result
        })
      });

      const data = await res.json();
      setChat([...chat, { q: query, a: data.answer }]);
    } catch {
      setChat([...chat, { q: query, a: "⚠️ AI error. Try again." }]);
    }

    setQuery("");
    setChatLoading(false);
  };

  // ✅ SAFE CHART DATA
  const chartData = result?.profile?.missing_values
  ? Object.entries(result.profile.missing_values).map(([k, v]) => ({
      name: k,
      mean: v
    }))
  : [];

  const pieData = chartData.slice(0, 5);

  const downloadReport = () => {
  if (!result) return;

  const blob = new Blob([JSON.stringify(result, null, 2)], {
    type: "application/json"
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "report.json";
  a.click();
};

const downloadCleanedData = async () => {
  if (!file) {
    alert("Upload file first");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("http://127.0.0.1:8001/api/clean", {
      method: "POST",
      body: formData
    });

    // 🔥 IMPORTANT: DO NOT CHECK res.json() FIRST
    if (!res.ok) {
      throw new Error("API failed");
    }

    // 🔥 HANDLE CSV RESPONSE
    if (file.name.endsWith(".csv")) {
      const blob = await res.blob();

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cleaned_data.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } 
    else {
      // JSON case
      const data = await res.json();

      const blob = new Blob(
        [JSON.stringify(data.cleaned_data, null, 2)],
        { type: "application/json" }
      );

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cleaned_data.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
    }

  } catch (err) {
    console.error(err);
    alert("Download failed. Check backend.");
  }
};

  return (
    <div style={{
      display: "flex",
      minHeight: "100vh",
      background: "linear-gradient(-45deg, #fbc2eb, #a6c1ee, #fbc2eb)",
      backgroundSize: "400% 400%",
      animation: "gradient 10s ease infinite"
    }}>

      {/* Sidebar */}
      <div style={{ width: 220, background: "rgba(255,255,255,0.2)", padding: 20 }}>
        <Typography variant="h6">✨ Menu</Typography>
        {["Overview","Insights","Cleaning Report","Reports","AI Chat","AI Story"].map((item, i) => (
          <div key={i}
            onClick={() => setTab(i)}
            style={{
              marginTop: 15,
              cursor: "pointer",
              color: tab===i?primary:"black"
            }}>
            {item}
          </div>
        ))}
      </div>

      {/* Main */}
      <Container maxWidth="lg">
        <Typography variant="h4" style={{ marginTop: 20 }}>
          🚀 AI Quality Governance Assistant
        </Typography>

        {/* Upload */}
        <motion.div
  {...getRootProps()}
  whileHover={{ scale: 1.05 }}
  style={{
    border: "2px dashed white",
    padding: 40,
    marginTop: 60,
    textAlign: "center",
    borderRadius: 15,
    background: "rgba(255,255,255,0.5)",
    width: "60%",
    marginLeft: "auto",
    marginRight: "auto"
  }}
>
          <input {...getInputProps()} />
          <Typography>📂 Upload Dataset</Typography>
          {file && <p>{file.name}</p>}
        </motion.div>

        {loading && <p>🤖 Processing...</p>}

        {/* Overview */}
        {tab === 0 && result && (
          <Card style={{ marginTop: 20 }}>
            <CardContent>
              <Typography>Rows: {result?.profile?.row_count || 0}</Typography>
              <Typography>Duplicates: {result?.profile?.duplicates || 0}</Typography>
              <LinearProgress variant="determinate" value={70} />
            </CardContent>
          </Card>
        )}

        {/* Insights */}
        {tab === 1 && (
  <>
    {result?.quality_score === 100 ? (

      // ✅ CLEAN DATA MESSAGE
      <Card style={{ marginTop: 20 }}>
        <CardContent>
          <Typography variant="h6">
            🎉 Dataset is perfectly clean!
          </Typography>

          <Typography style={{ marginTop: 10 }}>
            No missing values or inconsistencies detected.
          </Typography>

          <Typography style={{ marginTop: 10 }}>
            Your dataset is ready for analysis and publication 🚀
          </Typography>
        </CardContent>
      </Card>

    ) : (

      // 🔥 EXISTING CHARTS (UNCHANGED)
      <Grid
        container
        spacing={2}
        style={{
          marginTop: 20,
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <BarChart width={400} height={300} data={chartData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="mean" fill="#6366f1" />
              </BarChart>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <PieChart width={600} height={300}>
                <Pie
                  data={pieData}
                  dataKey="mean"
                  nameKey="name"
                  outerRadius={110}
                  label={({ name, percent }) =>
                    `${name.length > 10
                      ? name.substring(0, 10) + "..."
                      : name
                    } (${(percent * 100).toFixed(0)}%)`
                  }
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={colors[i % colors.length]} />
                  ))}
                </Pie>
              </PieChart>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

    )}
  </>
)}

        {/* Cleaning */}
        {tab === 2 && (
  <Card style={{ marginTop: 20 }}>
  <CardContent>

    <Typography variant="h6">🧹 Cleaning Report</Typography>

    {/* Issues */}
    <div style={{ marginTop: 10 }}>
      <Typography><b>⚠ Detected Issues:</b></Typography>
      <ul style={{ marginTop: 5 }}>
        {result?.issues?.map((issue, i) => (
          <li key={i}>{issue}</li>
        ))}
      </ul>
    </div>

    {/* Suggestions */}
    <div style={{ marginTop: 15 }}>
      <Typography><b>💡 Recommended Fixes:</b></Typography>
      <ul style={{ marginTop: 5 }}>
        {result?.suggestions?.map((s, i) => (
          <li key={i}>{s}</li>
        ))}
      </ul>
    </div>

  </CardContent>
</Card>
        )}
        {/* Reports */}
        {tab === 3 && (
  <Card style={{ marginTop: 20 }}>
    <CardContent>

      <Typography variant="h6">📊 Report Summary</Typography>

      <Typography>Rows: {result?.profile?.row_count}</Typography>
      <Typography>Quality Score: {result?.quality_score}%</Typography>
      <Typography>Total Issues: {result?.issues?.length}</Typography>

      <Button onClick={downloadReport} style={{ marginRight: 10 }}>Download Report</Button>
      <Button onClick={downloadCleanedData}>Download Cleaned Dataset</Button>

    </CardContent>
  </Card>
)}
        {/* Chat */}
        {tab === 4 && (
          <Card style={{ marginTop: 20 }}>
            <CardContent>

              <div style={{ maxHeight: 300, overflowY: "auto", padding: 10 }}>
  {chat.map((c, i) => (
    <div key={i} style={{ marginBottom: 15 }}>

      {/* USER */}
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <div style={{
          background: primary,
          color: "white",
          padding: "10px 14px",
          borderRadius: "18px 18px 4px 18px",
          maxWidth: "65%",
          fontSize: 14
        }}>
          {c.q}
        </div>
      </div>

      {/* AI */}
      <div style={{ display: "flex", justifyContent: "flex-start", marginTop: 6 }}>
        <div style={{
          background: secondary,
          padding: "12px 16px",
          borderRadius: "18px 18px 18px 4px",
          maxWidth: "70%",
          lineHeight: 1.6,
          whiteSpace: "pre-line",
          fontSize: 14
        }}>
          {c.a}
        </div>
      </div>

    </div>
  ))}
</div>
              

              {chatLoading && <p>🤖 AI typing...</p>}

              <div style={{ display:"flex", marginTop:10 }}>
                <TextField
                  fullWidth
                  value={query}
                  onChange={(e)=>setQuery(e.target.value)}
                />
                <Button onClick={sendQuery}>Send</Button>
              </div>

            </CardContent>
          </Card>
        )}

        {/* Story */}
        {tab === 5 && (
          <Card style={{ marginTop: 20 }}>
            <CardContent>
              <Typography style={{ lineHeight: 1.8 }}>
  <div>📊 <b>Dataset Size:</b> {result?.profile?.row_count} records</div>

  <div style={{ marginTop: 8 }}>
    ⚠ <b>Issues Detected:</b> {result?.issues?.length || 0} major issues including missing values and inconsistencies
  </div>

  <div style={{ marginTop: 8 }}>
    📉 <b>Quality Score:</b> {result?.quality_score}%
  </div>

  <div style={{ marginTop: 8 }}>
    💡 <b>Recommendations:</b> Automated cleaning such as handling missing values and correcting calculations
  </div>

  <div style={{ marginTop: 8 }}>
    🚀 <b>Outcome:</b> Dataset becomes reliable for analysis and publication after fixes
  </div>
</Typography>
            </CardContent>
          </Card>
        )}

      </Container>

      <style>{`
        @keyframes gradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
      `}</style>
    </div>
  );
}

export default App;