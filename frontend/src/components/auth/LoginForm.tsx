import React from 'react'
import { useForm } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Link,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Visibility, VisibilityOff, Email, Lock } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { loginUser, clearError } from '../../store/slices/authSlice'
import { useState, useEffect } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'

const schema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email address')
    .required('Email is required'),
  password: yup
    .string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required'),
})

type FormData = yup.InferType<typeof schema>

interface LoginFormProps {
  onSuccess?: () => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { isLoading, error, isAuthenticated } = useAppSelector((state) => state.auth)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
  })

  useEffect(() => {
    if (isAuthenticated) {
      onSuccess?.()
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate, onSuccess])

  useEffect(() => {
    // Clear error when component mounts
    dispatch(clearError())
  }, [dispatch])

  const onSubmit = async (data: FormData) => {
    dispatch(loginUser(data))
  }

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        maxWidth: 400,
        width: '100%',
        mx: 'auto',
        mt: 8,
      }}
    >
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Sign In
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Welcome back! Please sign in to your account.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <TextField
          {...register('email')}
          fullWidth
          label="Email Address"
          type="email"
          autoComplete="email"
          autoFocus
          margin="normal"
          error={!!errors.email}
          helperText={errors.email?.message}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Email color="action" />
              </InputAdornment>
            ),
          }}
        />

        <TextField
          {...register('password')}
          fullWidth
          label="Password"
          type={showPassword ? 'text' : 'password'}
          autoComplete="current-password"
          margin="normal"
          error={!!errors.password}
          helperText={errors.password?.message}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Lock color="action" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={handleTogglePasswordVisibility}
                  edge="end"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={isLoading}
          sx={{ mt: 3, mb: 2, py: 1.5 }}
        >
          {isLoading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            'Sign In'
          )}
        </Button>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Link
            component={RouterLink}
            to="/forgot-password"
            variant="body2"
            sx={{ display: 'block', mb: 1 }}
          >
            Forgot your password?
          </Link>
          <Typography variant="body2">
            Don't have an account?{' '}
            <Link component={RouterLink} to="/register">
              Sign up here
            </Link>
          </Typography>
        </Box>
      </Box>
    </Paper>
  )
}