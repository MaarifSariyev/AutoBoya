"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL, getFormula, calculateFormula } from "@/lib/api";
import { ArrowLeft, Calculator, Download, CheckCircle, Clock, AlertCircle } from "lucide-react";

interface Component {
  id: number;
  component_name: string;
  component_code: string;
  amount: number | string;
  unit: string;
  sort_order: number;
  percentage?: number;
  cumulative_amount?: number;
}

interface Formula {
  id: number;
  color_code: string;
  color_name: string;
  brand_name: string;
  model_name?: string;
  paint_system?: string;
  status: string;
  version: number;
  base_total_amount: number;
  expert_notes?: string;
  preparation_notes?: string;
  components: Component[];
}

interface CalcResult {
  target_amount: number;
  components: {
    component_name: string;
    component_code: string;
    amount: number | string;
    percentage: number | string;
    cumulative_amount: number | string;
  }[];
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  PUBLISHED: <CheckCircle className="h-4 w-4 text-green-400" />,
  VERIFIED: <CheckCircle className="h-4 w-4 text-blue-400" />,
  UNDER_REVIEW: <Clock className="h-4 w-4 text-yellow-400" />,
  DRAFT: <AlertCircle className="h-4 w-4 text-gray-400" />,
};

export default function FormulaDetail({ id }: { id: number }) {
  const [formula, setFormula] = useState<Formula | null>(null);
  const [loading, setLoading] = useState(true);
  const [targetAmount, setTargetAmount] = useState("");
  const [calcResult, setCalcResult] = useState<CalcResult | null>(null);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    let active = true;
    getFormula(id)
      .then((data) => { if (active) setFormula(data); })
      .catch(() => { if (active) setFormula(null); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id]);

  const handleCalculate = async () => {
    const amount = Number(targetAmount);
    if (!Number.isFinite(amount) || amount <= 0) return;
    setCalculating(true);
    try {
      const res = await calculateFormula(id, amount);
      setCalcResult(res);
    } catch {
      setCalcResult(null);
    } finally {
      setCalculating(false);
    }
  };

  const handlePdf = () => {
    window.open(
      `${API_URL}/api/formulas/${id}/pdf`,
      "_blank"
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white/50">Yüklənir...</div>
      </div>
    );
  }

  if (!formula) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center gap-4">
        <div className="text-white">Formul tapılmadı.</div>
        <Link href="/" className="text-blue-400 hover:underline">← Ana səhifə</Link>
      </div>
    );
  }

  const displayComponents = calcResult ? calcResult.components : null;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-white/10 bg-black/30 backdrop-blur sticky top-0 z-10">
        <div className="mx-auto max-w-4xl px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-white/60 hover:text-white transition-colors">
            <ArrowLeft className="h-4 w-4" />
            Axtarışa qayıt
          </Link>
          <button
            onClick={handlePdf}
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 border border-white/20 px-3 py-2 rounded-lg text-sm transition-colors"
          >
            <Download className="h-4 w-4" />
            PDF
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8 space-y-6">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="font-mono text-3xl font-bold text-blue-300">{formula.color_code}</span>
                {formula.paint_system && (
                  <span className="text-sm bg-blue-900/50 text-blue-300 px-2 py-1 rounded-full">
                    {formula.paint_system}
                  </span>
                )}
              </div>
              <h1 className="text-xl font-semibold">{formula.color_name}</h1>
              <p className="text-white/50 mt-1">
                {formula.brand_name}
                {formula.model_name && ` · ${formula.model_name}`}
                {` · v${formula.version}`}
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-sm">
              {STATUS_ICONS[formula.status]}
              <span className="text-white/60">{formula.status}</span>
            </div>
          </div>
          {(formula.preparation_notes || formula.expert_notes) && (
            <p className="text-white/50 text-sm border-t border-white/10 pt-4">{formula.preparation_notes || formula.expert_notes}</p>
          )}
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Calculator className="h-5 w-5 text-blue-400" />
            Kalkulyator
          </h2>
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-sm text-white/60 mb-1">
                Hazırlamaq istədiyiniz miqdar (qram)
              </label>
              <input
                type="number"
                min="0.1"
                step="0.1"
                placeholder={`Standart: ${formula.base_total_amount}g`}
                value={targetAmount}
                onChange={(e) => setTargetAmount(e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={handleCalculate}
              disabled={calculating || !targetAmount}
              className="self-end bg-blue-600 hover:bg-blue-500 disabled:opacity-40 px-5 py-2 rounded-lg font-medium transition-colors"
            >
              {calculating ? "..." : "Hesabla"}
            </button>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Komponentlər</h2>
            {calcResult && (
              <span className="text-sm text-blue-300 bg-blue-900/30 px-3 py-1 rounded-full">
                Hesablanmış: {calcResult.target_amount}g
              </span>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50">
                  <th className="text-left px-6 py-3">#</th>
                  <th className="text-left px-6 py-3">Komponent</th>
                  <th className="text-left px-6 py-3">Kod</th>
                  <th className="text-right px-6 py-3">Miqdar (g)</th>
                  {calcResult && (
                    <>
                      <th className="text-right px-6 py-3">Yeni Miqdar (g)</th>
                      <th className="text-right px-6 py-3">Kumulyativ (g)</th>
                    </>
                  )}
                  <th className="text-right px-6 py-3">%</th>
                </tr>
              </thead>
              <tbody>
                {formula.components.map((comp, i) => {
                  const calc = displayComponents?.[i];
                  const percentage = calc?.percentage ?? comp.percentage?.toFixed(2) ??
                    ((Number(comp.amount) / Number(formula.base_total_amount)) * 100).toFixed(2);
                  return (
                    <tr
                      key={comp.id}
                      className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <td className="px-6 py-3 text-white/30">{i + 1}</td>
                      <td className="px-6 py-3 font-medium">{comp.component_name}</td>
                      <td className="px-6 py-3 font-mono text-blue-300">{comp.component_code}</td>
                      <td className="px-6 py-3 text-right font-mono">{comp.amount}</td>
                      {calcResult && (
                        <>
                          <td className="px-6 py-3 text-right font-mono text-green-400">{calc?.amount}</td>
                          <td className="px-6 py-3 text-right font-mono text-yellow-300">{calc?.cumulative_amount}</td>
                        </>
                      )}
                      <td className="px-6 py-3 text-right text-white/50">{percentage}%</td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr className="border-t border-white/20 bg-white/5 font-semibold">
                  <td colSpan={3} className="px-6 py-3 text-white/60">Cəmi</td>
                  <td className="px-6 py-3 text-right font-mono">{formula.base_total_amount}g</td>
                  {calcResult && (
                    <>
                      <td className="px-6 py-3 text-right font-mono text-green-400">{calcResult.target_amount}g</td>
                      <td className="px-6 py-3 text-right"></td>
                    </>
                  )}
                  <td className="px-6 py-3 text-right">100%</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}