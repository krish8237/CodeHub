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
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Visibility, VisibilityOff, Lock } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { resetPassword, clearError } from '../../store/slices/authSlice'
import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'

const schema = yup.object({
  password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    )
    .required('Password is required'),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref('password')], 'Passwords must match')
    .required('Please confirm your password'),
})

type FormData = yup.InferType<typeof schema>

interface ResetPasswordFormProps {
  onSuccess?: () => void
}

export const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({ onSuccess }) => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isLoading, error } = useAppSelector((state) => state.auth)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const token = searchParams.get('token')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
  })

  useEffect(() => {
    // Clear error when component mounts
    dispatch(clearError())
    
    // Redirect if no token
    if (!token) {
      toast.error('Invalid or missing reset token')
      navigate('/forgot-password')
    }
  }, [dispatch, token, navigate])

  const onSubmit = async (data: FormData) => {
    if (!token) {
      toast.error('Invalid reset token')
      return
    }

    try {
      await dispatch(resetPassword({ token, password: data.password })).unwrap()
      toast.success('Password reset successful! You can now sign in with your new password.')
      onSuccess?.()
      navigate('/login')
    } catch (error) {
      // Error is handled by the slice
    }
  }

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  const handleToggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword)
  }

  if (!token) {
    return null
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
          Reset Password
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter your new password below.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <TextField
          {...register('password')}
          fullWidth
          label="New Password"
          type={showPassword ? 'text' : 'password'}
          autoComplete="new-password"
          autoFocus
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

        <TextField
          {...register('confirmPassword')}
          fullWidth
          label="Confirm New Password"
          type={showConfirmPassword ? 'text' : 'password'}
          autoComplete="new-password"
          margin="normal"
          error={!!errors.confirmPassword}
          helperText={errors.confirmPassword?.message}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Lock color="action" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle confirm password visibility"
                  onClick={handleToggleConfirmPasswordVisibility}
                  edge="end"
                >
                  {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
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
            'Reset Password'
          )}
        </Button>
      </Box>
    </Paper>
  )
}