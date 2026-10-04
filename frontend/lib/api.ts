import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// On 401 redirect to login
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      !window.location.pathname.includes("/admin/login")
    ) {
      localStorage.removeItem("access_token");
      window.location.replace("/admin/login");
    }
    return Promise.reject(error);
  }
);

// ─── Auth ───────────────────────────────────────────────────────────────────
export async function login(username: string, password: string) {
  const res = await api.post("/api/auth/login", { email: username, password });
  return res.data; // { access_token, token_type }
}

export async function getMe() {
  const res = await api.get("/api/auth/me");
  return res.data;
}

// ─── Public Search ──────────────────────────────────────────────────────────
export async function searchFormulas(params: {
  color_code?: string;
  color_name?: string;
  brand_id?: number;
  model_id?: number;
  year?: number;
  paint_system?: string;
  limit?: number;
  offset?: number;
}) {
  const res = await api.get("/api/formulas/search", { params });
  return res.data;
}

export async function getFormula(id: number) {
  const res = await api.get(`/api/formulas/${id}`);
  return res.data;
}

export async function calculateFormula(id: number, target_amount: number) {
  const res = await api.post(`/api/formulas/${id}/calculate`, {
    target_amount,
  });
  return res.data;
}

// ─── Public Lists ───────────────────────────────────────────────────────────
export async function getBrands() {
  const res = await api.get("/api/brands");
  return res.data;
}

export async function getModels(brand_id?: number) {
  const res = await api.get("/api/models", {
    params: brand_id ? { brand_id } : {},
  });
  return res.data;
}

// ─── Admin – Brands ─────────────────────────────────────────────────────────
export async function adminGetBrands(params = {}) {
  const res = await api.get("/api/brands/admin", { params });
  return res.data;
}
export async function adminCreateBrand(data: object) {
  const res = await api.post("/api/brands/admin", data);
  return res.data;
}
export async function adminUpdateBrand(id: number, data: object) {
  const res = await api.put(`/api/brands/admin/${id}`, data);
  return res.data;
}

// ─── Admin – Models ─────────────────────────────────────────────────────────
export async function adminGetModels(params = {}) {
  const res = await api.get("/api/models/admin", { params });
  return res.data;
}
export async function adminCreateModel(data: object) {
  const res = await api.post("/api/models/admin", data);
  return res.data;
}
export async function adminUpdateModel(id: number, data: object) {
  const res = await api.put(`/api/models/admin/${id}`, data);
  return res.data;
}

// ─── Admin – Colors ─────────────────────────────────────────────────────────
export async function adminGetColors(params = {}) {
  const res = await api.get("/api/colors/admin/all", { params });
  return res.data;
}
export async function adminCreateColor(data: object) {
  const res = await api.post("/api/colors/admin", data);
  return res.data;
}
export async function adminUpdateColor(id: number, data: object) {
  const res = await api.put(`/api/colors/admin/${id}`, data);
  return res.data;
}

// ─── Admin – Components ─────────────────────────────────────────────────────
export async function adminGetComponents(params = {}) {
  const res = await api.get("/api/components/admin", { params });
  return res.data;
}
export async function adminCreateComponent(data: object) {
  const res = await api.post("/api/components/admin", data);
  return res.data;
}
export async function adminUpdateComponent(id: number, data: object) {
  const res = await api.put(`/api/components/admin/${id}`, data);
  return res.data;
}

// ─── Admin – Formulas ───────────────────────────────────────────────────────
export async function adminGetFormulas(params = {}) {
  const res = await api.get("/api/formulas/admin/all", { params });
  return res.data;
}
export async function adminGetFormula(id: number) {
  const res = await api.get(`/api/formulas/admin/${id}`);
  return res.data;
}
export async function adminCreateFormula(data: object) {
  const res = await api.post("/api/formulas/admin", data);
  return res.data;
}
export async function adminUpdateFormula(id: number, data: object) {
  const res = await api.put(`/api/formulas/admin/${id}`, data);
  return res.data;
}
export async function adminVerifyFormula(id: number) {
  const res = await api.post(`/api/formulas/admin/${id}/verify`);
  return res.data;
}
export async function adminPublishFormula(id: number) {
  const res = await api.post(`/api/formulas/admin/${id}/publish`);
  return res.data;
}
export async function adminDeprecateFormula(id: number) {
  const res = await api.post(`/api/formulas/admin/${id}/deprecate`);
  return res.data;
}
export async function adminCreateVersion(id: number) {
  const res = await api.post(`/api/formulas/admin/${id}/version`);
  return res.data;
}

// ─── Admin – Import ─────────────────────────────────────────────────────────
export async function importPreview(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/api/admin/import/preview", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
export async function importConfirm(batch_id: string) {
  const res = await api.post("/api/admin/import/confirm", { batch_id });
  return res.data;
}

// ─── Admin – Stats / Audit ──────────────────────────────────────────────────
export async function getDashboardStats() {
  const res = await api.get("/api/admin/stats/dashboard");
  return res.data;
}
export async function getAuditLog(params = {}) {
  const res = await api.get("/api/admin/audit", { params });
  return res.data;
}
