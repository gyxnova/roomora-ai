import React, { useState, useEffect } from "react";

/**
 * Roomora AI — room design frontend.
 *
 * Form: photo (jpg/png/webp, mobile camera-friendly) + budget (INR) + style.
 * On submit: POST FormData to /api/design, show analysis card, plan table with
 * source badges, total vs budget, and a Telegraph receipts panel.
 */

const API = (import.meta.env.VITE_API_URL || "http://localhost:8000");

const STYLES = [
  { value: "minimalist",   label: "Minimalist" },
  { value: "modern",       label: "Modern" },
  { value: "japanese",     label: "Japanese" },
  { value: "scandinavian", label: "Scandinavian" },
  { value: "luxury",       label: "Luxury" },
];

/** Map price_source → badge label + CSS class */
function sourceBadge(item) {
  const src = (item.price_source || "").toLowerCase();
  if (src === "telegraph") {
    return { label: "Live via Telegraph", cls: "badge-live" };
  }
  if (src === "catalog" || src === "estimate") {
    return { label: "Estimate", cls: "badge-estimate" };
  }
  return { label: "MOCK", cls: "badge-mock" };
}

function SourceBadge({ item }) {
  const { label, cls } = sourceBadge(item);
  return <span className={`badge ${cls}`}>{label}</span>;
}

/** Format an integer as "₹1,23,456" (Indian locale) */
function inr(n) {
  return "₹" + Number(n).toLocaleString("en-IN");
}

export default function App() {
  // --- form state ---
  const [photo, setPhoto]     = useState(null);
  const [photoUrl, setPhotoUrl] = useState("");
  const [budget, setBudget]   = useState("");
  const [style, setStyle]     = useState("modern");

  // --- async state ---
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");
  const [design, setDesign]       = useState(null);

  // --- receipts panel ---
  const [receipts, setReceipts]           = useState([]);
  const [receiptsLoading, setReceiptsLoading] = useState(false);
  const [receiptsError, setReceiptsError]   = useState("");
  const [showReceipts, setShowReceipts]     = useState(false);

  // -----------------------------------------------------------------------
  // Handlers
  // -----------------------------------------------------------------------

  const handlePhotoChange = (e) => {
    const file = e.target.files?.[0];
    setPhoto(file || null);
    setError("");
    setDesign(null);
    setPhotoUrl(file ? URL.createObjectURL(file) : "");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setDesign(null);

    if (!photo) {
      setError("Please choose a room photo.");
      return;
    }
    const budgetNum = parseInt(budget, 10);
    if (!budget || isNaN(budgetNum)) {
      setError("Please enter a valid budget.");
      return;
    }

    const fd = new FormData();
    fd.append("photo", photo);
    fd.append("budget_inr", budgetNum);
    fd.append("style", style);

    setLoading(true);
    try {
      const resp = await fetch(`${API}/api/design`, { method: "POST", body: fd });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data?.detail || `Server error ${resp.status}`);
      }
      setDesign(data);
    } catch (err) {
      setError(err.message || "Failed to reach the backend.");
    } finally {
      setLoading(false);
    }
  };

  const loadReceipts = async () => {
    setShowReceipts(true);
    setReceiptsLoading(true);
    setReceiptsError("");
    try {
      const resp = await fetch(`${API}/api/receipts`);
      const data = await resp.json();
      if (!resp.ok) throw new Error(data?.detail || `Error ${resp.status}`);
      setReceipts(data);
    } catch (err) {
      setReceiptsError(err.message || "Could not load receipts.");
    } finally {
      setReceiptsLoading(false);
    }
  };

  // -----------------------------------------------------------------------
  // Render helpers
  // -----------------------------------------------------------------------

  const plan   = design?.design_plan || {};
  const items  = plan.items || [];
  const totalInr  = plan.total_inr ?? 0;
  const budgetInr = plan.budget_inr ?? design?.budget_inr ?? 0;
  const withinBudget    = plan.within_budget ?? true;
  const alternativesUsed = plan.alternatives_used ?? false;

  // -----------------------------------------------------------------------
  // JSX
  // -----------------------------------------------------------------------

  return (
    <div className="app">
      {/* ---------------------------------------------------------------- */}
      {/* Header                                                           */}
      {/* ---------------------------------------------------------------- */}
      <header>
        <h1>Roomora AI 🛋️</h1>
        <p className="subtitle">
          Upload a room photo, set your budget, pick a style — get an AI-curated
          furniture plan with live Telegraph prices.
        </p>
        <p className="privacy-note">📷 Upload photos without people in them.</p>
      </header>

      {/* ---------------------------------------------------------------- */}
      {/* Upload form                                                       */}
      {/* ---------------------------------------------------------------- */}
      <div className="card">
        <form onSubmit={handleSubmit}>
          <label htmlFor="photo-input">Room photo</label>
          <input
            id="photo-input"
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handlePhotoChange}
            required
          />
          {photoUrl && (
            <img src={photoUrl} alt="Room preview" className="preview show" />
          )}

          <label htmlFor="budget-input">Budget (INR)</label>
          <input
            id="budget-input"
            type="number"
            min="5000"
            max="5000000"
            step="1000"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            placeholder="e.g. 50000"
            required
          />
          <p className="field-hint">Between ₹5,000 and ₹50,00,000</p>

          <label htmlFor="style-select">Style</label>
          <select
            id="style-select"
            value={style}
            onChange={(e) => setStyle(e.target.value)}
          >
            {STYLES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>

          <button type="submit" className="primary" disabled={loading}>
            {loading ? "Generating design…" : "Generate design"}
          </button>
        </form>

        {/* Loading spinner */}
        {loading && (
          <p className="loading">⏳ Analysing your room and building the plan…</p>
        )}

        {/* Error */}
        {error && <div className="error">⚠️ {error}</div>}
      </div>

      {/* ---------------------------------------------------------------- */}
      {/* Results                                                           */}
      {/* ---------------------------------------------------------------- */}
      {design && (
        <>
          {/* Telegraph banner */}
          <div className="telegraph-banner">
            ⚡ Prices marked <strong>Live</strong> come from a Telegraph testnet
            purchase.
          </div>

          {/* Analysis card */}
          <div className="card">
            <h3>Room analysis</h3>
            <p>{design.analysis_summary}</p>
            <div className="meta-row">
              <span><strong>Style:</strong> {design.style}</span>
              <span><strong>Status:</strong> {design.status}</span>
            </div>
          </div>

          {/* Plan table */}
          <div className="card">
            <h3>Furniture plan</h3>

            {/* Budget summary */}
            <div className={`budget-bar ${withinBudget ? "ok" : "over"}`}>
              <span>Total: <strong>{inr(totalInr)}</strong></span>
              <span>Budget: <strong>{inr(budgetInr)}</strong></span>
              <span className="budget-status">
                {withinBudget ? "✅ Within budget" : "❌ Over budget"}
              </span>
            </div>

            {alternativesUsed && (
              <p className="alt-note">
                ℹ️ No catalog items matched your style exactly — showing
                alternatives from the full catalog.
              </p>
            )}

            {items.length === 0 ? (
              <p className="note">No items fit within this budget.</p>
            ) : (
              <table className="plan-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Price (INR)</th>
                    <th>Source</th>
                    <th>Receipt</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.id}>
                      <td>{item.name}</td>
                      <td>{inr(item.price_inr)}</td>
                      <td><SourceBadge item={item} /></td>
                      <td className="receipt-cell">
                        {item.receipt_id
                          ? <span className="receipt-id">{item.receipt_id}</span>
                          : <span className="text-muted">—</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td><strong>Total</strong></td>
                    <td><strong>{inr(totalInr)}</strong></td>
                    <td colSpan={2}></td>
                  </tr>
                </tfoot>
              </table>
            )}

            {plan.notes && <p className="note">{plan.notes}</p>}
          </div>
        </>
      )}

      {/* ---------------------------------------------------------------- */}
      {/* Telegraph receipts panel                                          */}
      {/* ---------------------------------------------------------------- */}
      <div className="card">
        <div className="receipts-header">
          <h3>Telegraph receipts</h3>
          <button className="secondary" onClick={loadReceipts} disabled={receiptsLoading}>
            {receiptsLoading ? "Loading…" : showReceipts ? "Refresh" : "Load receipts"}
          </button>
        </div>

        {receiptsError && <div className="error">{receiptsError}</div>}

        {showReceipts && !receiptsLoading && (
          receipts.length === 0 ? (
            <p className="note">No designs yet. Submit a photo above to get started.</p>
          ) : (
            <table className="plan-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Style</th>
                  <th>Budget</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {receipts.map((r) => (
                  <tr key={r.id}>
                    <td>{r.id}</td>
                    <td style={{ textTransform: "capitalize" }}>{r.style}</td>
                    <td>{inr(r.budget_inr)}</td>
                    <td>
                      <span className={`badge ${r.status === "done" ? "badge-live" : "badge-mock"}`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="text-muted">{r.created_at?.slice(0, 16) ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}
      </div>
    </div>
  );
}
