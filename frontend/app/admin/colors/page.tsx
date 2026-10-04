"use client";

import { useCallback, useEffect, useState } from "react";
import { adminGetColors, adminCreateColor, adminUpdateColor, adminGetBrands, adminGetModels } from "@/lib/api";
import { CrudTable } from "@/components/CrudTable";
import { Modal } from "@/components/Modal";

interface Brand { id: number; name: string; }
interface VehicleModel { id: number; name: string; }
interface Color {
  id: number;
  color_code: string;
  color_name: string;
  brand_id: number;
  model_id?: number | null;
  brand_name?: string;
  color_type: string;
  paint_system?: string;
  is_active: boolean;
}

const COLOR_TYPES = ["Solid", "Metallic", "Pearl", "Matte", "Candy", "Other", "Unknown"];
const PAINT_SYSTEMS = ["Standox", "Sikkens", "Glasurit", "Spies Hecker", "Cromax", "Nexa Autocolor", "PPG", "Other"];
const empty = { color_code: "", color_name: "", brand_id: "", model_id: "", color_type: "Metallic", paint_system: "", is_active: true };

export default function ColorsPage() {
  const [colors, setColors] = useState<Color[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [models, setModels] = useState<VehicleModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Color | null>(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    Promise.all([adminGetColors({ limit: 200 }), adminGetBrands({ limit: 200 })])
      .then(([c, b]) => { setColors(c.items ?? c); setBrands(b.items ?? b); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (!form.brand_id) return;
    let active = true;
    adminGetModels({ brand_id: form.brand_id })
      .then((m) => { if (active) setModels(m.items ?? m); })
      .catch(() => { if (active) setModels([]); });
    return () => { active = false; };
  }, [form.brand_id]);

  const openAdd = () => { setEditing(null); setForm(empty); setModels([]); setError(""); setModalOpen(true); };
  const openEdit = (c: Color) => {
    setEditing(c);
    setModels([]);
    setForm({ color_code: c.color_code, color_name: c.color_name, brand_id: String(c.brand_id), model_id: c.model_id ? String(c.model_id) : "", color_type: c.color_type, paint_system: c.paint_system ?? "", is_active: c.is_active });
    setError("");
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    const payload = { ...form, brand_id: Number(form.brand_id), model_id: form.model_id ? Number(form.model_id) : null, paint_system: form.paint_system || "Basecoat" };
    try {
      if (editing) await adminUpdateColor(editing.id, payload);
      else await adminCreateColor(payload);
      setModalOpen(false);
      setLoading(true);
      load();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Xəta baş verdi.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <CrudTable
        title="Rənglər"
        data={colors}
        loading={loading}
        onAdd={openAdd}
        onEdit={openEdit}
        columns={[
          { header: "ID", accessor: "id", className: "w-16 text-white/30" },
          { header: "Kod", accessor: (r) => <span className="font-mono text-blue-300">{r.color_code}</span> },
          { header: "Ad", accessor: "color_name" },
          { header: "Marka", accessor: (r) => r.brand_name || String(r.brand_id) },
          { header: "Növ", accessor: "color_type" },
          { header: "Sistem", accessor: (r) => r.paint_system || "—" },
          { header: "Status", accessor: (r) => <span className={`text-xs px-2 py-0.5 rounded-full ${r.is_active ? "bg-green-900/40 text-green-300" : "bg-red-900/40 text-red-300"}`}>{r.is_active ? "Aktiv" : "Deaktiv"}</span> },
        ]}
      />

      <Modal title={editing ? "Rəng redaktə et" : "Yeni rəng"} open={modalOpen} onClose={() => setModalOpen(false)}>
        <form onSubmit={handleSave} className="space-y-4">
          {error && <div className="bg-red-900/30 border border-red-500/30 text-red-300 rounded-lg px-4 py-2 text-sm">{error}</div>}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-white/60 mb-1">Rəng Kodu *</label>
              <input required type="text" placeholder="1G3" value={form.color_code} onChange={(e) => setForm({ ...form, color_code: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Rəng Adı *</label>
              <input required type="text" placeholder="Gümüşü" value={form.color_name} onChange={(e) => setForm({ ...form, color_name: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm text-white/60 mb-1">Marka *</label>
            <select required value={form.brand_id} onChange={(e) => { setModels([]); setForm({ ...form, brand_id: e.target.value, model_id: "" }); }} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="" className="bg-slate-800">Seçin</option>
              {brands.map((b) => <option key={b.id} value={b.id} className="bg-slate-800">{b.name}</option>)}
            </select>
          </div>
          {models.length > 0 && (
            <div>
              <label className="block text-sm text-white/60 mb-1">Model (istəyə bağlı)</label>
              <select value={form.model_id} onChange={(e) => setForm({ ...form, model_id: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="" className="bg-slate-800">— Hamısı —</option>
                {models.map((m) => <option key={m.id} value={m.id} className="bg-slate-800">{m.name}</option>)}
              </select>
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-white/60 mb-1">Rəng Növü</label>
              <select value={form.color_type} onChange={(e) => setForm({ ...form, color_type: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                {COLOR_TYPES.map((t) => <option key={t} value={t} className="bg-slate-800">{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Boya Sistemi</label>
              <select value={form.paint_system} onChange={(e) => setForm({ ...form, paint_system: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="" className="bg-slate-800">— Seçin —</option>
                {PAINT_SYSTEMS.map((s) => <option key={s} value={s} className="bg-slate-800">{s}</option>)}
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="is_active_c" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} className="w-4 h-4 rounded accent-blue-500" />
            <label htmlFor="is_active_c" className="text-sm text-white/70">Aktiv</label>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)} className="flex-1 bg-white/10 hover:bg-white/20 text-white py-2 rounded-lg text-sm transition-colors">Ləğv et</button>
            <button type="submit" disabled={saving} className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium transition-colors">{saving ? "Saxlanır..." : "Saxla"}</button>
          </div>
        </form>
      </Modal>
    </>
  );
}
