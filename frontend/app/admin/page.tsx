"use client";

import { useEffect, useState } from "react";
import { getDashboardStats } from "@/lib/api";
import { Tag, Car, Palette, FlaskConical, Package, CheckCircle } from "lucide-react";

interface Stats {
  total_brands: number;
  total_models: number;
  total_colors: number;
  total_formulas: number;
  total_components: number;
  published_formulas: number;
  draft_formulas: number;
  under_review_formulas: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    getDashboardStats().then(setStats).catch(() => {});
  }, []);

  const cards = stats
    ? [
        { label: "Markalar", value: stats.total_brands, icon: Tag, color: "text-blue-400" },
        { label: "Modellər", value: stats.total_models, icon: Car, color: "text-purple-400" },
        { label: "Rənglər", value: stats.total_colors, icon: Palette, color: "text-pink-400" },
        { label: "Komponentlər", value: stats.total_components, icon: Package, color: "text-orange-400" },
        { label: "Formullar", value: stats.total_formulas, icon: FlaskConical, color: "text-cyan-400" },
        { label: "Yayımlanmış", value: stats.published_formulas, icon: CheckCircle, color: "text-green-400" },
      ]
    : [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Dashboard</h1>

      {!stats ? (
        <div className="text-white/40">Yüklənir...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            {cards.map(({ label, value, icon: Icon, color }) => (
              <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-4">
                <Icon className={`h-5 w-5 ${color} mb-2`} />
                <div className="text-2xl font-bold text-white">{value}</div>
                <div className="text-xs text-white/40 mt-1">{label}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: "Qaralama", value: stats.draft_formulas, color: "bg-gray-500/20 text-gray-300" },
              { label: "Yoxlanılır", value: stats.under_review_formulas, color: "bg-yellow-500/20 text-yellow-300" },
              { label: "Yayımlanmış", value: stats.published_formulas, color: "bg-green-500/20 text-green-300" },
            ].map(({ label, value, color }) => (
              <div key={label} className={`rounded-xl p-5 ${color} border border-white/10`}>
                <div className="text-3xl font-bold">{value}</div>
                <div className="text-sm mt-1 opacity-70">{label} formul</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
