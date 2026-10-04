"use client";

import { useCallback, useEffect, useState } from "react";
import { adminGetComponents, adminCreateComponent, adminUpdateComponent } from "@/lib/api";
import { CrudTable } from "@/components/CrudTable";
import { Modal } from "@/components/Modal";

interface Component {
  id: number;
  name: string;
  code: string;
  unit: string;
  brand?: string;
  category?: string;
  is_active: boolean;
}

const empty = { name: "", code: "", unit: "g", brand: "", category: "", is_active: true };

export default function ComponentsPage() {
  const [items, setItems] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Component | null>(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    adminGetComponents({ limit: 500 })
      .then((d) => setItems(d.items ?? d))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const openAdd = () => { setEditing(null); setForm(empty); setError(""); setModalOpen(true); };
  const openEdit = (c: Component) => {
    setEditing(c);
    setForm({ name: c.name, code: c.code, unit: c.unit, brand: c.brand ?? "", category: c.category ?? "", is_active: c.is_active });
    setError("");
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (editing) await adminUpdateComponent(editing.id, form);
      else await adminCreateComponent(form);
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
        title="Komponentlər"
        data={items}
        loading={loading}
        onAdd={openAdd}
        onEdit={openEdit}
        columns={[
          { header: "ID", accessor: "id", className: "w-16 text-white/30" },
          { header: "Ad", accessor: "name" },
          { header: "Kod", accessor: (r) => <span className="font-mono text-blue-300">{r.code}</span> },
          { header: "Vahid", accessor: "unit" },
          { header: "Brend", accessor: (r) => r.brand || "—" },
          { header: "Kateqoriya", accessor: (r) => r.category || "—" },
          { header: "Status", accessor: (r) => <span className={`text-xs px-2 py-0.5 rounded-full ${r.is_active ? "bg-green-900/40 text-green-300" : "bg-red-900/40 text-red-300"}`}>{r.is_active ? "Aktiv" : "Deaktiv"}</span> },
        ]}
      />

      <Modal title={editing ? "Komponenti redaktə et" : "Yeni komponent"} open={modalOpen} onClose={() => setModalOpen(false)}>
        <form onSubmit={handleSave} className="space-y-4">
          {error && <div className="bg-red-900/30 border border-red-500/30 text-red-300 rounded-lg px-4 py-2 text-sm">{error}</div>}
          {[
            { label: "Ad", key: "name", placeholder: "Carbon Black", required: true },
            { label: "Kod", key: "code", placeholder: "CB-1", required: true },
            { label: "Vahid", key: "unit", placeholder: "g", required: true },
            { label: "Brend", key: "brand", placeholder: "BASF" },
            { label: "Kateqoriya", key: "category", placeholder: "Metallic toner" },
          ].map(({ label, key, placeholder, required }) => (
            <div key={key}>
              <label className="block text-sm text-white/60 mb-1">{label}{required && " *"}</label>
              <input type="text" required={required} placeholder={placeholder} value={form[key as keyof typeof form] as string} onChange={(e) => setForm({ ...form, [key]: e.target.value })} className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          ))}
          <div className="flex items-center gap-2">
            <input type="checkbox" id="is_active_comp" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} className="w-4 h-4 rounded accent-blue-500" />
            <label htmlFor="is_active_comp" className="text-sm text-white/70">Aktiv</label>
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
