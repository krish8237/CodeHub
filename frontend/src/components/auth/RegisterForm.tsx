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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
} from '@mui/material'
import { Visibility, VisibilityOff, Email, Lock, Person } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { registerUser, clearError } from '../../store/slices/authSlice'
import { useState, useEffect } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import toast from 'react-hot-toast'

const schema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email address')
    .required('Email is required'),
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
  role: yup
    .string()
    .oneOf(['student', 'instructor'], 'Please select a valid role')
    .required('Role is required'),
})

type FormData = yup.InferType<typeof schema>

interface RegisterFormProps {
  onSuccess?: () => void
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { isLoading, error } = useAppSelector((state) => state.auth)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      role: 'student',
    },
  })

  useEffect(() => {
    // Clear error when component mounts
    dispatch(clearError())
  }, [dispatch])

  const onSubmit = async (data: FormData) => {
    try {
      await dispatch(registerUser(data)).unwrap()
      toast.success('Registration successful! Please check your email to verify your account.')
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

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        maxWidth: 450,
        width: '100%',
        mx: 'auto',
        mt: 8,
      }}
    >
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Create Account
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Join our assessment platform today!
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

        <FormControl fullWidth margin="normal" error={!!errors.role}>
          <InputLabel id="role-label">Role</InputLabel>
          <Select
            {...register('role')}
            labelId="role-label"
            label="Role"
            defaultValue="student"
            startAdornment={
              <InputAdornment position="start">
                <Person color="action" />
              </InputAdornment>
            }
          >
            <MenuItem value="student">Student</MenuItem>
            <MenuItem value="instructor">Instructor</MenuItem>
          </Select>
          {errors.role && (
            <FormHelperText>{errors.role.message}</FormHelperText>
          )}
        </FormControl>

        <TextField
          {...register('password')}
          fullWidth
          label="Password"
          type={showPassword ? 'text' : 'password'}
          autoComplete="new-password"
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
          label="Confirm Password"
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
            'Create Account'
          )}
        </Button>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2">
            Already have an account?{' '}
            <Link component={RouterLink} to="/login">
              Sign in here
            </Link>
          </Typography>
        </Box>
      </Box>
    </Paper>
  )
}