"use client";

import { useCallback, useEffect, useState } from "react";
import { getAuditLog } from "@/lib/api";

interface AuditEntry {
  id: number;
  action: string;
  entity: string;
  entity_id: string;
  user_email: string;
  timestamp: string;
  details?: string;
}

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 50;

  const load = useCallback((p: number) => {
    getAuditLog({ limit: PAGE_SIZE, offset: (p - 1) * PAGE_SIZE })
      .then((d) => {
        setLogs(Array.isArray(d) ? d : d.items ?? []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(page); }, [load, page]);

  const ACTION_COLORS: Record<string, string> = {
    CREATE: "text-green-400",
    UPDATE: "text-blue-400",
    DELETE: "text-red-400",
    LOGIN: "text-yellow-400",
    STATUS_CHANGE: "text-purple-400",
  };

  const fmt = (iso: string) => new Date(iso).toLocaleString("az-AZ");

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Audit Jurnalı</h1>

      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-white/40">Yüklənir...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-white/40">Qeyd tapılmadı.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50">
                  <th className="text-left px-4 py-3">Tarix</th>
                  <th className="text-left px-4 py-3">İstifadəçi</th>
                  <th className="text-left px-4 py-3">Əməliyyat</th>
                  <th className="text-left px-4 py-3">Cədvəl</th>
                  <th className="text-left px-4 py-3">Qeyd ID</th>
                  <th className="text-left px-4 py-3">Detallar</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="px-4 py-3 text-white/50 whitespace-nowrap">{fmt(log.timestamp)}</td>
                    <td className="px-4 py-3 text-white/70">{log.user_email}</td>
                    <td className={`px-4 py-3 font-medium ${ACTION_COLORS[log.action] ?? "text-white/70"}`}>{log.action}</td>
                    <td className="px-4 py-3 text-white/60 font-mono text-xs">{log.entity}</td>
                    <td className="px-4 py-3 text-white/40 font-mono text-xs">{log.entity_id}</td>
                    <td className="px-4 py-3 text-white/40 text-xs max-w-xs truncate">
                      {log.details ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {(page > 1 || logs.length === PAGE_SIZE) && (
        <div className="flex items-center justify-between mt-4 text-sm">
          <span className="text-white/40">Səhifə {page}</span>
          <div className="flex gap-2">
            <button
              onClick={() => { setLoading(true); setPage((p) => Math.max(1, p - 1)); }}
              disabled={page === 1}
              className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-30 text-white transition-colors"
            >
              ← Geri
            </button>
            <span className="px-3 py-1.5 text-white/60">{page}</span>
            <button
              onClick={() => { setLoading(true); setPage((p) => p + 1); }}
              disabled={logs.length < PAGE_SIZE}
              className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-30 text-white transition-colors"
            >
              İrəli →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
