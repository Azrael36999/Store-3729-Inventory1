import React, { useEffect, useMemo, useState } from "react";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import { getToken } from "./auth";

export default function App() {
  const [token, setToken] = useState<string | null>(getToken());

  if (!token) return <LoginPage onAuthed={setToken} />;

  return <Dashboard token={token} onLogout={() => { localStorage.removeItem("token"); setToken(null); }} />;
}
