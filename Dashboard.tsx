import React, { useEffect, useMemo, useState } from "react";
import { fetchSettings, fetchItems, fetchUnits, uuidv4, pushSync, pullSync } from "../api";
import { queueEvent } from "../db";

function formatCase(base: number, caseSize?: number | null) {
  if (!caseSize || caseSize <= 0) return `${base.toFixed(2)}`;
  const cases = Math.floor(base / caseSize);
  const rem = base - cases * caseSize;
  if (cases === 0) return `${rem.toFixed(2)}`;
  if (rem === 0) return `${cases} case`;
  return `${cases} case + ${rem.toFixed(2)}`;
}

export default function Dashboard({ token, onLogout }: { token: string; onLogout: ()=>void }) {
  const [settings, setSettings] = useState<any>(null);
  const [units, setUnits] = useState<any[]>([]);
  const [items, setItems] = useState<any[]>([]);
  const [deviceId, setDeviceId] = useState<string>(() => localStorage.getItem("deviceId") || uuidv4());
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    localStorage.setItem("deviceId", deviceId);
    (async () => {
      const s = await fetchSettings(token);
      setSettings(s);
      const u = await fetchUnits(token);
      setUnits(u.filter((x:any)=>x.active));
      const it = await fetchItems(token);
      setItems(it);
    })();
  }, [token]);

  async function doSync() {
    setStatus("Syncing...");
    await pushSync(token, deviceId);
    await pullSync(token);
    setStatus("Synced");
    setTimeout(()=>setStatus(""), 1200);
  }

  async function addItemQuick() {
    const name = prompt("Item name?");
    if (!name) return;
    const baseUnitId = units[0]?.id;
    if (!baseUnitId) { alert("No units found. Check Supabase seed."); return; }
    // For now, create items from UI by queueing an adjustment? No: use API in later iteration.
    alert("Item creation UI is in the next step. For now, create items in the Items page (coming next).");
  }

  async function adjustmentFlow() {
    if (!items.length) { alert("Add items first (Items page coming next)."); return; }
    const q = prompt("Search item name (type part of it):");
    if (!q) return;
    const match = items.find(i => i.name.toLowerCase().includes(q.toLowerCase()));
    if (!match) { alert("No match."); return; }
    const deltaStr = prompt("Adjustment delta in BASE units (e.g. +3 or -2).\n(Next version supports cases + base entry.)");
    if (!deltaStr) return;
    const delta = Number(deltaStr);
    if (Number.isNaN(delta) || delta === 0) { alert("Invalid delta."); return; }
    const notes = prompt("Notes (optional):") || null;

    const evt = {
      client_event_id: uuidv4(),
      event_type: "ADJUSTMENT",
      item_id: match.id,
      delta_base_units: delta,
      notes,
      ref_type: "adjustment",
      ref_id: null,
      photo_url: null
    };
    await queueEvent(evt);
    setStatus("Saved offline (queued). Tap Sync when online.");
  }

  return (
    <div style={{ padding: 16, fontFamily: "system-ui" }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <div>
          <h2 style={{ margin: 0 }}>Store 3729 Inventory</h2>
          {settings && <div style={{ opacity: 0.75 }}>{settings.store_label} — {settings.intersection}</div>}
        </div>
        <button onClick={onLogout}>Logout</button>
      </div>

      <div style={{ marginTop: 12, display:"flex", gap: 8, flexWrap:"wrap" }}>
        <button onClick={doSync}>Sync</button>
        <button onClick={adjustmentFlow}>Quick Adjustment</button>
        <button onClick={()=>alert("Items CRUD screen is the next build step. This starter focuses on auth + offline sync queue.")}>Items</button>
        <button onClick={()=>alert("Transfers screen is next step.")}>Borrow/Lend</button>
        <button onClick={()=>alert("Count + Truck Receive is next step.")}>Count / Truck</button>
      </div>

      {status && <div style={{ marginTop: 10, opacity: 0.8 }}>{status}</div>}

      <hr style={{ margin: "16px 0" }} />

      <h3 style={{ marginBottom: 6 }}>What’s in this starter</h3>
      <ul>
        <li>Shared login</li>
        <li>Offline event queue (multi-device safe)</li>
        <li>Sync push/pull</li>
        <li>Quick Adjustment (base units for now)</li>
      </ul>

      <p style={{ opacity: 0.75 }}>
        Next build step adds full: Items CRUD + smart units (cases + base) + Borrow/Lend tickets + Count sessions + Low Stock page.
      </p>
    </div>
  );
}
