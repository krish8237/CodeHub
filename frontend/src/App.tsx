import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import { CodingDemoPage } from './pages/CodingDemoPage'

// Components will be created in later tasks
// import { Layout } from '@/components/Layout'
// import { ProtectedRoute } from '@/components/ProtectedRoute'
// import { LoginPage } from '@/pages/auth/LoginPage'
// import { DashboardPage } from '@/pages/DashboardPage'

function App() {
  return (
    <Box sx={{ minHeight: '100vh' }}>
      <Routes>
        <Route path="/" element={<div>Welcome to Assessment Platform</div>} />
        <Route path="/health" element={<div>Application is running</div>} />
        <Route path="/coding-demo" element={<CodingDemoPage />} />
        {/* Routes will be added in later tasks */}
        {/* <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        /> */}
      </Routes>
    </Box>
  )
}

export default App