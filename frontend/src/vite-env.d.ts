/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_ENVIRONMENT: string
  readonly VITE_ENABLE_ANALYTICS: string
  readonly VITE_ENABLE_TUTORIALS: string
  readonly VITE_ENABLE_EXPORT: string
  readonly VITE_MONACO_EDITOR_CDN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}