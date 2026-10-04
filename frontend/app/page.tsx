"use client";

import { useState, useEffect } from "react";
import { getBrands, getModels, searchFormulas } from "@/lib/api";
import Link from "next/link";
import { Search, ChevronRight, Palette, Database, CheckCircle } from "lucide-react";

interface Brand { id: number; name: string; country?: string; }
interface Model { id: number; name: string; year_from?: number; year_to?: number; }
interface FormulaResult {
  id: number;
  color_code: string;
  color_name: string;
  brand_name: string;
  model_name?: string;
  paint_system?: string;
  status: string;
  version: number;
}

export default function HomePage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [results, setResults] = useState<FormulaResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    color_code: "",
    color_name: "",
    brand_id: "",
    model_id: "",
    year: "",
    paint_system: "",
  });

  useEffect(() => {
    getBrands().then(setBrands).catch(() => {});
  }, []);

  useEffect(() => {
    if (!form.brand_id) return;
    let active = true;
    getModels(Number(form.brand_id))
      .then((data) => { if (active) setModels(data); })
      .catch(() => { if (active) setModels([]); });
    return () => { active = false; };
  }, [form.brand_id]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const params: Record<string, string | number> = {};
      if (form.color_code) params.color_code = form.color_code;
      if (form.color_name) params.color_name = form.color_name;
      if (form.brand_id) params.brand_id = Number(form.brand_id);
      if (form.model_id) params.model_id = Number(form.model_id);
      if (form.year) params.year = Number(form.year);
      if (form.paint_system) params.paint_system = form.paint_system;
      const data = await searchFormulas(params);
      setResults(Array.isArray(data) ? data : data.results || []);
      setSearched(true);
    } catch {
      setResults([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Palette className="h-7 w-7 text-blue-400" />
            <span className="text-xl font-bold text-white">AutoBoya</span>
          </div>
          <Link
            href="/admin/login"
            className="text-sm text-white/60 hover:text-white transition-colors"
          >
            Admin Panel →
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-4xl px-4 py-16 text-center">
        <h1 className="text-4xl font-extrabold text-white mb-4">
          Avtomobil Boya Formulları
        </h1>
        <p className="text-lg text-white/60 mb-10">
          Rəng kodu, marka və model üzrə axtarın — dəqiq formulu anında əldə edin
        </p>

        {/* Search Form */}
        <form
          onSubmit={handleSearch}
          className="bg-white/10 backdrop-blur border border-white/20 rounded-2xl p-6 text-left space-y-4"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white/70 mb-1">Rəng Kodu</label>
              <input
                type="text"
                placeholder="məs. 1G3, NH0, W55"
                value={form.color_code}
                onChange={(e) => setForm({ ...form, color_code: e.target.value })}
                className="w-full rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/30 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-white/70 mb-1">Rəng Adı</label>
              <input
                type="text"
                placeholder="məs. Gümüşü, Qara"
                value={form.color_name}
                onChange={(e) => setForm({ ...form, color_name: e.target.value })}
                className="w-full rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/30 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-white/70 mb-1">Marka</label>
              <select
                value={form.brand_id}
                onChange={(e) => { setModels([]); setForm({ ...form, brand_id: e.target.value, model_id: "" }); }}
                className="w-full rounded-lg bg-white/10 border border-white/20 text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="" className="bg-slate-800">Bütün markalar</option>
                {brands.map((b) => (
                  <option key={b.id} value={b.id} className="bg-slate-800">
                    {b.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-white/70 mb-1">Model</label>
              <select
                value={form.model_id}
                onChange={(e) => setForm({ ...form, model_id: e.target.value })}
                disabled={!form.brand_id}
                className="w-full rounded-lg bg-white/10 border border-white/20 text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-40"
              >
                <option value="" className="bg-slate-800">Bütün modellər</option>
                {models.map((m) => (
                  <option key={m.id} value={m.id} className="bg-slate-800">
                    {m.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-white/70 mb-1">İl</label>
              <input
                type="number"
                placeholder="məs. 2020"
                min={1990}
                max={2030}
                value={form.year}
                onChange={(e) => setForm({ ...form, year: e.target.value })}
                className="w-full rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/30 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-white/70 mb-1">Boya Sistemi</label>
              <select
                value={form.paint_system}
                onChange={(e) => setForm({ ...form, paint_system: e.target.value })}
                className="w-full rounded-lg bg-white/10 border border-white/20 text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="" className="bg-slate-800">Hamısı</option>
                <option value="Standox" className="bg-slate-800">Standox</option>
                <option value="Sikkens" className="bg-slate-800">Sikkens</option>
                <option value="Glasurit" className="bg-slate-800">Glasurit</option>
                <option value="Spies Hecker" className="bg-slate-800">Spies Hecker</option>
                <option value="Cromax" className="bg-slate-800">Cromax</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            <Search className="h-4 w-4" />
            {loading ? "Axtarılır..." : "Axtar"}
          </button>
        </form>
      </section>

      {/* Results */}
      {searched && (
        <section className="mx-auto max-w-4xl px-4 pb-16">
          {results.length === 0 ? (
            <div className="text-center text-white/50 py-8">Heç bir nəticə tapılmadı.</div>
          ) : (
            <div className="space-y-3">
              <p className="text-white/50 text-sm mb-4">{results.length} nəticə tapıldı</p>
              {results.map((r) => (
                <Link
                  key={r.id}
                  href={`/formula?id=${r.id}`}
                  className="flex items-center justify-between bg-white/10 hover:bg-white/15 border border-white/20 rounded-xl px-5 py-4 transition-colors group"
                >
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono font-bold text-blue-300 text-lg">
                        {r.color_code}
                      </span>
                      {r.paint_system && (
                        <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded-full">
                          {r.paint_system}
                        </span>
                      )}
                    </div>
                    <div className="text-white font-medium">{r.color_name}</div>
                    <div className="text-white/50 text-sm">
                      {r.brand_name}
                      {r.model_name && ` · ${r.model_name}`}
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-white/30 group-hover:text-white/70 transition-colors" />
                </Link>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Features (shown before search) */}
      {!searched && (
        <section className="mx-auto max-w-4xl px-4 pb-16">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { icon: Database, title: "Geniş Baza", desc: "Azərbaycanda ən çox istifadə olunan markalar üzrə formul bazası" },
              { icon: CheckCircle, title: "Doğrulanmış", desc: "Hər formul mütəxəssis tərəfindən yoxlanılır və təsdiqlənir" },
              { icon: Palette, title: "Kalkulyator", desc: "İstənilən miqdar üçün komponent kəmiyyətlərini avtomatik hesablayın" },
            ].map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="bg-white/5 border border-white/10 rounded-xl p-5"
              >
                <Icon className="h-6 w-6 text-blue-400 mb-3" />
                <h3 className="text-white font-semibold mb-1">{title}</h3>
                <p className="text-white/50 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
