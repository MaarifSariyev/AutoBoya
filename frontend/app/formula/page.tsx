"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import FormulaDetail from "@/components/FormulaDetail";

export default function FormulaRoute() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-900 flex items-center justify-center text-white/50">Yüklənir...</div>}>
      <FormulaRouteContent />
    </Suspense>
  );
}

function FormulaRouteContent() {
  const searchParams = useSearchParams();
  const formulaId = Number(searchParams.get("id"));

  if (!Number.isInteger(formulaId) || formulaId <= 0) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center gap-4">
        <div className="text-white">Formul tapılmadı.</div>
        <Link href="/" className="text-blue-400 hover:underline">← Ana səhifə</Link>
      </div>
    );
  }

  return <FormulaDetail id={formulaId} />;
}