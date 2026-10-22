// Wire envelope shared by mock and future module-backed API responses.
// /health and binary GLB downloads are intentionally outside this envelope.
export interface ApiError {
  code: string;
  message: string;
  details: { field: string; message: string }[];
}

export type ApiResponse<T> =
  | { data: T; error: null }
  | { data: null; error: ApiError };
