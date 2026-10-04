"use client";

import { useCallback, useEffect, useState } from "react";
import { adminGetModels, adminCreateModel, adminUpdateModel, adminGetBrands } from "@/lib/api";
import { CrudTable } from "@/components/CrudTable";
import { Modal } from "@/components/Modal";

interface Brand { id: number; name: string; }
interface Model {
  id: number;
  name: string;
  brand_id: number;
  brand_name?: string;
  year_from?: number;
  year_to?: number;
  is_active: boolean;
}

const empty = { name: "", brand_id: "", year_from: "", year_to: "", is_active: true };

export default function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Model | null>(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    Promise.all([
      adminGetModels(),
      adminGetBrands({ limit: 200 }),
    ])
      .then(([m, b]) => {
        setModels(m.items ?? m);
        setBrands(b.items ?? b);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const openAdd = () => {
    setEditing(null);
    setForm(empty);
    setError("");
    setModalOpen(true);
  };

  const openEdit = (m: Model) => {
    setEditing(m);
    setForm({
      name: m.name,
      brand_id: String(m.brand_id),
      year_from: m.year_from ? String(m.year_from) : "",
      year_to: m.year_to ? String(m.year_to) : "",
      is_active: m.is_active,
    });
    setError("");
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    const payload = {
      name: form.name,
      brand_id: Number(form.brand_id),
      year_from: form.year_from ? Number(form.year_from) : null,
      year_to: form.year_to ? Number(form.year_to) : null,
      is_active: form.is_active,
    };
    try {
      if (editing) await adminUpdateModel(editing.id, payload);
      else await adminCreateModel(payload);
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
        title="Modellər"
        data={models}
        loading={loading}
        onAdd={openAdd}
        onEdit={openEdit}
        columns={[
          { header: "ID", accessor: "id", className: "w-16 text-white/30" },
          { header: "Ad", accessor: "name" },
          { header: "Marka", accessor: (r) => r.brand_name || String(r.brand_id) },
          { header: "İllər", accessor: (r) => `${r.year_from ?? "?"} – ${r.year_to ?? "..."}` },
          {
            header: "Status",
            accessor: (r) => (
              <span className={`text-xs px-2 py-0.5 rounded-full ${r.is_active ? "bg-green-900/40 text-green-300" : "bg-red-900/40 text-red-300"}`}>
                {r.is_active ? "Aktiv" : "Deaktiv"}
              </span>
            ),
          },
        ]}
      />

      <Modal title={editing ? "Model redaktə et" : "Yeni model"} open={modalOpen} onClose={() => setModalOpen(false)}>
        <form onSubmit={handleSave} className="space-y-4">
          {error && <div className="bg-red-900/30 border border-red-500/30 text-red-300 rounded-lg px-4 py-2 text-sm">{error}</div>}
          <div>
            <label className="block text-sm text-white/60 mb-1">Marka *</label>
            <select required value={form.brand_id} onChange={(e) => setForm({ ...form, brand_id: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="" className="bg-slate-800">Seçin</option>
              {brands.map((b) => <option key={b.id} value={b.id} className="bg-slate-800">{b.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-white/60 mb-1">Model adı *</label>
            <input required type="text" placeholder="Camry" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-white/60 mb-1">İlk il</label>
              <input type="number" placeholder="2015" value={form.year_from} onChange={(e) => setForm({ ...form, year_from: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Son il</label>
              <input type="number" placeholder="2023" value={form.year_to} onChange={(e) => setForm({ ...form, year_to: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="is_active" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} className="w-4 h-4 rounded accent-blue-500" />
            <label htmlFor="is_active" className="text-sm text-white/70">Aktiv</label>
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
