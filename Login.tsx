import React, { useState } from "react";
import { login } from "../api";
import { saveToken } from "../auth";

export default function LoginPage({ onAuthed }: { onAuthed: (t: string) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const data = await login(username, password);
      saveToken(data.token);
      onAuthed(data.token);
    } catch {
      setErr("Login failed. Check username/password.");
    }
  }

  return (
    <div style={{ padding: 16, maxWidth: 420, margin: "0 auto", fontFamily: "system-ui" }}>
      <h2>Store 3729 Inventory</h2>
      <p style={{ marginTop: -8, opacity: 0.7 }}>Shared login</p>
      <form onSubmit={submit}>
        <label>Username</label><br />
        <input value={username} onChange={e=>setUsername(e.target.value)} style={{ width:"100%", padding: 10, marginBottom: 10 }} />
        <label>Password</label><br />
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} style={{ width:"100%", padding: 10, marginBottom: 10 }} />
        <button style={{ width:"100%", padding: 12 }}>Login</button>
        {err && <div style={{ color:"crimson", marginTop: 10 }}>{err}</div>}
      </form>
    </div>
  );
}
