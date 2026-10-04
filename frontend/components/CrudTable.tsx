"use client";

import { Pencil, Plus } from "lucide-react";

interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  className?: string;
}

interface Props<T extends { id: number }> {
  title: string;
  data: T[];
  columns: Column<T>[];
  onAdd?: () => void;
  onEdit?: (row: T) => void;
  loading?: boolean;
  addLabel?: string;
}

export function CrudTable<T extends { id: number }>({
  title, data, columns, onAdd, onEdit, loading, addLabel = "Yeni əlavə et"
}: Props<T>) {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {onAdd && (
          <button
            onClick={onAdd}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="h-4 w-4" />
            {addLabel}
          </button>
        )}
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-white/40">Yüklənir...</div>
        ) : data.length === 0 ? (
          <div className="p-8 text-center text-white/40">Məlumat tapılmadı.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50">
                  {columns.map((col) => (
                    <th
                      key={String(col.accessor)}
                      className={`text-left px-4 py-3 font-medium ${col.className ?? ""}`}
                    >
                      {col.header}
                    </th>
                  ))}
                  {onEdit && <th className="px-4 py-3 w-16"></th>}
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    {columns.map((col) => (
                      <td
                        key={String(col.accessor)}
                        className={`px-4 py-3 text-white/80 ${col.className ?? ""}`}
                      >
                        {typeof col.accessor === "function"
                          ? col.accessor(row)
                          : String(row[col.accessor] ?? "—")}
                      </td>
                    ))}
                    {onEdit && (
                      <td className="px-4 py-3">
                        <button
                          onClick={() => onEdit(row)}
                          className="text-white/30 hover:text-white transition-colors"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
