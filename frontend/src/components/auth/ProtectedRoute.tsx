import React, { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Box, CircularProgress, Typography } from '@mui/material'
import { useAppSelector, useAppDispatch } from '../../store/hooks'
import { getCurrentUser } from '../../store/slices/authSlice'

interface ProtectedRouteProps {
  children: React.ReactNode
  roles?: ('student' | 'instructor' | 'admin')[]
  requireAuth?: boolean
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  roles,
  requireAuth = true,
}) => {
  const dispatch = useAppDispatch()
  const location = useLocation()
  const { user, token, isAuthenticated, isLoading } = useAppSelector((state) => state.auth)

  useEffect(() => {
    // If we have a token but no user, try to get current user
    if (token && !user && !isLoading) {
      dispatch(getCurrentUser())
    }
  }, [token, user, isLoading, dispatch])

  // Show loading spinner while checking authentication
  if (isLoading || (token && !user)) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={40} />
        <Typography variant="body1" color="text.secondary">
          Loading...
        </Typography>
      </Box>
    )
  }

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // If specific roles are required, check user role
  if (roles && user && !roles.includes(user.role)) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
          p: 3,
        }}
      >
        <Typography variant="h5" color="error">
          Access Denied
        </Typography>
        <Typography variant="body1" color="text.secondary" textAlign="center">
          You don't have permission to access this page.
          {roles.length === 1 
            ? ` This page requires ${roles[0]} role.`
            : ` This page requires one of the following roles: ${roles.join(', ')}.`
          }
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Your current role: {user.role}
        </Typography>
      </Box>
    )
  }

  return <>{children}</>
}

// Higher-order component for role-based access
export const withRoleProtection = (
  Component: React.ComponentType<any>,
  roles: ('student' | 'instructor' | 'admin')[]
) => {
  return (props: any) => (
    <ProtectedRoute roles={roles}>
      <Component {...props} />
    </ProtectedRoute>
  )
}

// Specific role protection components
export const StudentRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute roles={['student']}>{children}</ProtectedRoute>
)

export const InstructorRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute roles={['instructor']}>{children}</ProtectedRoute>
)

export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute roles={['admin']}>{children}</ProtectedRoute>
)

export const InstructorOrAdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute roles={['instructor', 'admin']}>{children}</ProtectedRoute>
)