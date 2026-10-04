"use client";

import { useState } from "react";
import { API_URL, importPreview, importConfirm } from "@/lib/api";
import { Upload, CheckCircle, AlertCircle, Download } from "lucide-react";

interface PreviewItem {
  row_number: number;
  color_code: string;
  color_name: string;
  brand: string;
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

interface PreviewResult {
  batch_id: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  total_formulas_detected: number;
  errors: string[];
  sample_preview: PreviewItem[];
  can_proceed: boolean;
}

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const handlePreview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    setPreview(null);
    setDone(false);
    try {
      const res = await importPreview(file);
      setPreview(res);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Fayl oxunarkən xəta baş verdi.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!preview) return;
    setConfirming(true);
    setError("");
    try {
      await importConfirm(preview.batch_id);
      setDone(true);
      setPreview(null);
      setFile(null);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Təsdiq zamanı xəta baş verdi.");
    } finally {
      setConfirming(false);
    }
  };

  const templateUrl = `${API_URL}/api/admin/import/template`;

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">CSV/XLSX İdxal</h1>
        <a
          href={templateUrl}
          download
          className="flex items-center gap-2 bg-white/10 hover:bg-white/20 border border-white/20 text-white/70 hover:text-white px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <Download className="h-4 w-4" />
          Şablon yüklə
        </a>
      </div>

      {done && (
        <div className="bg-green-900/30 border border-green-500/30 text-green-300 rounded-xl px-5 py-4 mb-6 flex items-center gap-3">
          <CheckCircle className="h-5 w-5 flex-shrink-0" />
          <span>İdxal uğurla tamamlandı!</span>
        </div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-500/30 text-red-300 rounded-xl px-5 py-4 mb-6 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Step 1: Upload */}
      {!preview && (
        <form onSubmit={handlePreview} className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Addım 1: Fayl seçin</h2>
          <label className="flex flex-col items-center justify-center w-full h-36 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:border-blue-500/50 transition-colors bg-white/5">
            <Upload className="h-8 w-8 text-white/30 mb-2" />
            <span className="text-white/50 text-sm">{file ? file.name : "CSV və ya XLSX fayl seçin"}</span>
            <input
              type="file"
              accept=".csv,.xlsx"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
          <button
            type="submit"
            disabled={!file || loading}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {loading ? "Yüklənir..." : "Önizlə"}
          </button>
        </form>
      )}

      {/* Step 2: Preview */}
      {preview && (
        <div className="space-y-4">
          {preview.errors.length > 0 && (
            <div className="bg-red-900/30 border border-red-500/30 text-red-300 rounded-xl px-5 py-4">
              {preview.errors.map((message) => <p key={message}>{message}</p>)}
            </div>
          )}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Addım 2: Nəticəni yoxlayın</h2>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-white/5 rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-white">{preview.total_rows}</div>
                <div className="text-xs text-white/40 mt-1">Ümumi sətir</div>
              </div>
              <div className="bg-green-900/20 rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-green-400">{preview.valid_rows}</div>
                <div className="text-xs text-white/40 mt-1">Düzgün</div>
              </div>
              <div className="bg-red-900/20 rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-red-400">{preview.invalid_rows}</div>
                <div className="text-xs text-white/40 mt-1">Xətalı</div>
              </div>
            </div>

            <div className="max-h-64 overflow-y-auto space-y-1.5">
              {preview.sample_preview.map((item) => (
                <div
                  key={item.row_number}
                  className={`flex items-start gap-3 text-sm px-3 py-2 rounded-lg ${
                    item.is_valid ? "bg-green-900/20 text-green-300" : "bg-red-900/20 text-red-300"
                  }`}
                >
                  {item.is_valid ? (
                    <CheckCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  )}
                  <span>
                    Sətir {item.row_number}: <span className="font-mono">{item.color_code}</span> — {item.color_name}
                    {item.errors.length > 0 && <span className="text-red-300/80"> ({item.errors.join("; ")})</span>}
                    {item.warnings.length > 0 && <span className="text-yellow-300/80"> ({item.warnings.join("; ")})</span>}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setPreview(null)}
              className="flex-1 bg-white/10 hover:bg-white/20 text-white py-2.5 rounded-lg text-sm transition-colors"
            >
              Ləğv et
            </button>
            <button
              onClick={handleConfirm}
              disabled={confirming || !preview.can_proceed}
              className="flex-1 bg-green-600 hover:bg-green-500 disabled:opacity-40 text-white font-medium py-2.5 rounded-lg transition-colors"
            >
              {confirming ? "İdxal edilir..." : `${preview.valid_rows} sətir idxal et`}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
