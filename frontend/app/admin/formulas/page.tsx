"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  adminGetFormulas, adminCreateFormula, adminUpdateFormula,
  adminVerifyFormula, adminPublishFormula, adminDeprecateFormula,
  adminCreateVersion, adminGetColors, adminGetComponents, adminGetFormula,
} from "@/lib/api";
import { Modal } from "@/components/Modal";
import { Plus, Pencil, Globe, Archive, GitBranch, FlaskConical, ExternalLink } from "lucide-react";

interface Formula {
  id: number;
  color_id: number;
  formula_name: string;
  variant_name: string;
  color_code: string;
  color_name: string;
  brand_name?: string;
  paint_system?: string;
  status: string;
  version: number;
  base_total_amount: number;
}
interface Color { id: number; color_code: string; color_name: string; brand_name?: string; }
interface Component { id: number; name: string; code: string; unit: string; }

const STATUS_COLORS: Record<string, string> = {
  DRAFT: "bg-gray-500/20 text-gray-300",
  UNDER_REVIEW: "bg-yellow-500/20 text-yellow-300",
  VERIFIED: "bg-blue-500/20 text-blue-300",
  PUBLISHED: "bg-green-500/20 text-green-300",
  DEPRECATED: "bg-red-500/20 text-red-300",
};

const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Qaralama",
  UNDER_REVIEW: "Yoxlanılır",
  VERIFIED: "Doğrulanmış",
  PUBLISHED: "Yayımlanmış",
  DEPRECATED: "Köhnəlmiş",
};

interface FormulaComponentRow {
  component_id: number;
  component_name: string;
  component_code: string;
  amount: string;
  order_index: number;
}

export default function FormulasPage() {
  const [formulas, setFormulas] = useState<Formula[]>([]);
  const [colors, setColors] = useState<Color[]>([]);
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Formula | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [form, setForm] = useState({
    color_id: "",
    paint_system: "",
    base_total_amount: "500",
    notes: "",
    source_type: "EXPERT_CREATED",
  });
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [rows, setRows] = useState<FormulaComponentRow[]>([
    { component_id: 0, component_name: "", component_code: "", amount: "", order_index: 1 },
  ]);

  const load = useCallback(() => {
    const params: Record<string, string | number> = { limit: 500 };
    if (statusFilter) params.status = statusFilter;
    Promise.all([
      adminGetFormulas(params),
      adminGetColors({ limit: 200 }),
      adminGetComponents({ limit: 500 }),
    ])
      .then(([f, c, comp]) => {
        setFormulas(f.items ?? f);
        setColors(c.items ?? c);
        setComponents(comp.items ?? comp);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [statusFilter]);

  useEffect(() => { load(); }, [load]);

  const openAdd = () => {
    setEditing(null);
    setForm({ color_id: "", paint_system: "", base_total_amount: "500", notes: "", source_type: "EXPERT_CREATED" });
    setRows([{ component_id: 0, component_name: "", component_code: "", amount: "", order_index: 1 }]);
    setError("");
    setModalOpen(true);
  };

  const openEdit = async (f: Formula) => {
    setEditing(f);
    setForm({ color_id: String(f.color_id), paint_system: f.paint_system ?? "", base_total_amount: String(f.base_total_amount), notes: "", source_type: "EXPERT_CREATED" });
    setRows([]);
    setError("");
    setModalOpen(true);
    setLoadingDetails(true);
    try {
      const details = await adminGetFormula(f.id);
      setForm({
        color_id: String(details.color_id),
        paint_system: details.paint_system,
        base_total_amount: String(details.base_total_amount),
        notes: details.expert_notes ?? "",
        source_type: details.source_type,
      });
      setRows(details.components.map((component: { component_code: string; component_name: string; amount: string | number; sort_order: number }) => {
        const libraryComponent = components.find((item) => item.code === component.component_code);
        return {
          component_id: libraryComponent?.id ?? 0,
          component_name: component.component_name,
          component_code: component.component_code,
          amount: String(component.amount),
          order_index: component.sort_order,
        };
      }));
    } catch {
      setError("Formul məlumatları yüklənə bilmədi.");
    } finally {
      setLoadingDetails(false);
    }
  };

  const addRow = () => setRows((r) => [...r, { component_id: 0, component_name: "", component_code: "", amount: "", order_index: r.length + 1 }]);
  const removeRow = (i: number) => setRows((r) => r.filter((_, idx) => idx !== i));

  const setRowComponent = (i: number, compId: number) => {
    const comp = components.find((c) => c.id === compId);
    setRows((r) =>
      r.map((row, idx) =>
        idx === i
          ? { ...row, component_id: compId, component_name: comp?.name ?? "", component_code: comp?.code ?? "" }
          : row
      )
    );
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const selectedColor = colors.find((color) => color.id === Number(form.color_id));
    const validRows = rows.filter((row) => row.component_name && row.component_code && row.amount.trim());
    if (loadingDetails || validRows.length === 0) {
      setError("Ən azı bir komponent seçin və miqdar daxil edin.");
      return;
    }
    if (!editing && !selectedColor) {
      setError("Rəng seçin.");
      return;
    }
    const componentTotal = validRows.reduce((total, row) => total + Number(row.amount), 0);
    if (Math.abs(componentTotal - Number(form.base_total_amount)) > 0.001) {
      setError(`Komponentlərin cəmi (${componentTotal.toFixed(4)} g) əsas miqdara uyğun olmalıdır.`);
      return;
    }
    setSaving(true);
    setError("");
    const payload = {
      color_id: Number(form.color_id),
      formula_name: editing?.formula_name ?? `${selectedColor?.color_code} ${selectedColor?.color_name}`,
      variant_name: editing?.variant_name ?? "Standard",
      paint_system: form.paint_system || "Basecoat",
      base_total_amount: Number(form.base_total_amount),
      unit: "g",
      expert_notes: form.notes || null,
      source_type: form.source_type,
      components: validRows
        .map((r, i) => ({
          component_code: r.component_code,
          component_name: r.component_name,
          amount: Number(r.amount),
          unit: components.find((component) => component.id === r.component_id)?.unit ?? "g",
          sort_order: i,
        })),
    };
    try {
      if (editing) await adminUpdateFormula(editing.id, payload);
      else await adminCreateFormula(payload);
      setModalOpen(false);
      setLoading(true);
      load();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof msg === "string" ? msg : JSON.stringify(msg) || "Xəta baş verdi.");
    } finally {
      setSaving(false);
    }
  };

  const handleAction = async (id: number, action: "verify" | "publish" | "deprecate" | "version") => {
    try {
      if (action === "verify") await adminVerifyFormula(id);
      else if (action === "publish") await adminPublishFormula(id);
      else if (action === "deprecate") await adminDeprecateFormula(id);
      else await adminCreateVersion(id);
      setLoading(true);
      load();
    } catch {
      alert("Əməliyyat uğursuz oldu.");
    }
  };

  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-white">Formullar</h1>
        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => { setLoading(true); setStatusFilter(e.target.value); }}
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="" className="bg-slate-800">Bütün statuslar</option>
            {Object.entries(STATUS_LABELS).map(([k, v]) => (
              <option key={k} value={k} className="bg-slate-800">{v}</option>
            ))}
          </select>
          <button onClick={openAdd} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Plus className="h-4 w-4" />
            Yeni formul
          </button>
        </div>
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-white/40">Yüklənir...</div>
        ) : formulas.length === 0 ? (
          <div className="p-8 text-center text-white/40">Formul tapılmadı.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50">
                  <th className="text-left px-4 py-3">Kod</th>
                  <th className="text-left px-4 py-3">Rəng</th>
                  <th className="text-left px-4 py-3">Marka</th>
                  <th className="text-left px-4 py-3">Sistem</th>
                  <th className="text-left px-4 py-3">Status</th>
                  <th className="text-left px-4 py-3">Ver.</th>
                  <th className="text-left px-4 py-3">Əməliyyatlar</th>
                </tr>
              </thead>
              <tbody>
                {formulas.map((f) => (
                  <tr key={f.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="px-4 py-3 font-mono text-blue-300">{f.color_code}</td>
                    <td className="px-4 py-3 text-white">{f.color_name}</td>
                    <td className="px-4 py-3 text-white/60">{f.brand_name ?? "—"}</td>
                    <td className="px-4 py-3 text-white/60">{f.paint_system ?? "—"}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[f.status] ?? ""}`}>
                        {STATUS_LABELS[f.status] ?? f.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-white/50">v{f.version}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <Link href={`/formula?id=${f.id}`} target="_blank" title="Bax" className="text-white/30 hover:text-white transition-colors">
                          <ExternalLink className="h-4 w-4" />
                        </Link>
                        <button onClick={() => openEdit(f)} title="Redaktə" className="text-white/30 hover:text-white transition-colors">
                          <Pencil className="h-4 w-4" />
                        </button>
                        {f.status === "DRAFT" && (
                          <button onClick={() => handleAction(f.id, "verify")} title="Doğrula" className="text-white/30 hover:text-blue-400 transition-colors">
                            <FlaskConical className="h-4 w-4" />
                          </button>
                        )}
                        {f.status === "VERIFIED" && (
                          <button onClick={() => handleAction(f.id, "publish")} title="Yayımla" className="text-white/30 hover:text-green-400 transition-colors">
                            <Globe className="h-4 w-4" />
                          </button>
                        )}
                        {(f.status === "PUBLISHED" || f.status === "VERIFIED") && (
                          <button onClick={() => handleAction(f.id, "deprecate")} title="Köhnəlt" className="text-white/30 hover:text-red-400 transition-colors">
                            <Archive className="h-4 w-4" />
                          </button>
                        )}
                        <button onClick={() => handleAction(f.id, "version")} title="Yeni versiya" className="text-white/30 hover:text-yellow-400 transition-colors">
                          <GitBranch className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal title={editing ? `Formul redaktə: ${editing.color_code}` : "Yeni formul"} open={modalOpen} onClose={() => setModalOpen(false)}>
        <form onSubmit={handleSave} className="space-y-4">
          {error && <div className="bg-red-900/30 border border-red-500/30 text-red-300 rounded-lg px-4 py-2 text-sm">{error}</div>}

          {!editing && (
            <div>
              <label className="block text-sm text-white/60 mb-1">Rəng *</label>
              <select required value={form.color_id} onChange={(e) => setForm({ ...form, color_id: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="" className="bg-slate-800">Seçin</option>
                {colors.map((c) => <option key={c.id} value={c.id} className="bg-slate-800">{c.color_code} — {c.color_name} ({c.brand_name})</option>)}
              </select>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-white/60 mb-1">Boya Sistemi</label>
              <input type="text" placeholder="Standox" value={form.paint_system} onChange={(e) => setForm({ ...form, paint_system: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Əsas Miqdar (g) *</label>
              <input required type="number" step="0.01" min="0" value={form.base_total_amount} onChange={(e) => setForm({ ...form, base_total_amount: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>

          <div>
            <label className="block text-sm text-white/60 mb-1">Qeyd</label>
            <textarea rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
          </div>

          {/* Component rows */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-white/60">Komponentlər</label>
              <button type="button" onClick={addRow} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                <Plus className="h-3 w-3" /> Əlavə et
              </button>
            </div>
            <div className="space-y-2">
              {rows.map((row, i) => (
                <div key={i} className="flex gap-2 items-center">
                  <select
                    value={row.component_id || (row.component_code ? "existing" : "")}
                    onChange={(e) => { if (e.target.value !== "existing") setRowComponent(i, Number(e.target.value)); }}
                    className="flex-1 bg-white/10 border border-white/20 rounded-lg px-2 py-1.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="" className="bg-slate-800">Komponent seçin</option>
                    {row.component_id === 0 && row.component_code && <option value="existing" className="bg-slate-800">{row.component_name} ({row.component_code})</option>}
                    {components.map((c) => <option key={c.id} value={c.id} className="bg-slate-800">{c.name} ({c.code})</option>)}
                  </select>
                  <input
                    type="number"
                    step="0.0001"
                    min="0"
                    placeholder="Miqdar"
                    value={row.amount}
                    onChange={(e) => setRows((r) => r.map((row2, idx) => idx === i ? { ...row2, amount: e.target.value } : row2))}
                    className="w-24 bg-white/10 border border-white/20 rounded-lg px-2 py-1.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {rows.length > 1 && (
                    <button type="button" onClick={() => removeRow(i)} className="text-white/30 hover:text-red-400 text-lg leading-none">×</button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)} className="flex-1 bg-white/10 hover:bg-white/20 text-white py-2 rounded-lg text-sm transition-colors">Ləğv et</button>
            <button type="submit" disabled={saving || loadingDetails} className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium transition-colors">{loadingDetails ? "Yüklənir..." : saving ? "Saxlanır..." : "Saxla"}</button>
          </div>
        </form>
      </Modal>
    </>
  );
}
