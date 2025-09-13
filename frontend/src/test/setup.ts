import '@testing-library/jest-dom'

// Mock environment variables
Object.defineProperty(window, 'import.meta', {
  value: {
    env: {
      VITE_API_BASE_URL: 'http://localhost:8000/api/v1',
      VITE_WS_URL: 'ws://localhost:8000/ws',
      VITE_ENVIRONMENT: 'test',
    },
  },
})

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange }: any) => (
    <textarea
      data-testid="monaco-editor"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
    />
  ),
}))

// Mock Chart.js
vi.mock('react-chartjs-2', () => ({
  Line: () => <div data-testid="line-chart" />,
  Bar: () => <div data-testid="bar-chart" />,
  Pie: () => <div data-testid="pie-chart" />,
}))

// Global test utilities
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))