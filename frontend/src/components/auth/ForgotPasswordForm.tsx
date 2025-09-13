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
} from '@mui/material'
import { Email, ArrowBack } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { requestPasswordReset, clearError } from '../../store/slices/authSlice'
import { useState, useEffect } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import toast from 'react-hot-toast'

const schema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email address')
    .required('Email is required'),
})

type FormData = yup.InferType<typeof schema>

interface ForgotPasswordFormProps {
  onSuccess?: () => void
}

export const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({ onSuccess }) => {
  const dispatch = useAppDispatch()
  const { isLoading, error } = useAppSelector((state) => state.auth)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<FormData>({
    resolver: yupResolver(schema),
  })

  useEffect(() => {
    // Clear error when component mounts
    dispatch(clearError())
  }, [dispatch])

  const onSubmit = async (data: FormData) => {
    try {
      await dispatch(requestPasswordReset(data.email)).unwrap()
      setIsSubmitted(true)
      toast.success('Password reset instructions sent to your email!')
      onSuccess?.()
    } catch (error) {
      // Error is handled by the slice
    }
  }

  if (isSubmitted) {
    return (
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 400,
          width: '100%',
          mx: 'auto',
          mt: 8,
          textAlign: 'center',
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom color="primary">
          Check Your Email
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          We've sent password reset instructions to{' '}
          <strong>{getValues('email')}</strong>
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Please check your email and follow the instructions to reset your password.
          If you don't see the email, check your spam folder.
        </Typography>
        <Button
          component={RouterLink}
          to="/login"
          variant="outlined"
          startIcon={<ArrowBack />}
          fullWidth
        >
          Back to Sign In
        </Button>
      </Paper>
    )
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
          Forgot Password
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter your email address and we'll send you instructions to reset your password.
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
            'Send Reset Instructions'
          )}
        </Button>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Link
            component={RouterLink}
            to="/login"
            variant="body2"
            sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <ArrowBack sx={{ mr: 1, fontSize: 16 }} />
            Back to Sign In
          </Link>
        </Box>
      </Box>
    </Paper>
  )
}