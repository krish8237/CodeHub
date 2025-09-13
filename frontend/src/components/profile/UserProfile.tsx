import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Divider,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  InputAdornment,
  IconButton,
} from '@mui/material'
import {
  Person,
  Email,
  CalendarToday,
  Edit,
  Save,
  Cancel,
  Lock,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../../store/hooks'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import axios from 'axios'

const profileSchema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email address')
    .required('Email is required'),
})

const passwordSchema = yup.object({
  currentPassword: yup
    .string()
    .required('Current password is required'),
  newPassword: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    )
    .required('New password is required'),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref('newPassword')], 'Passwords must match')
    .required('Please confirm your password'),
})

type ProfileFormData = yup.InferType<typeof profileSchema>
type PasswordFormData = yup.InferType<typeof passwordSchema>

export const UserProfile: React.FC = () => {
  const { user, token } = useAppSelector((state) => state.auth)
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false)
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    register: registerProfile,
    handleSubmit: handleSubmitProfile,
    formState: { errors: profileErrors },
    reset: resetProfile,
  } = useForm<ProfileFormData>({
    resolver: yupResolver(profileSchema),
    defaultValues: {
      email: user?.email || '',
    },
  })

  const {
    register: registerPassword,
    handleSubmit: handleSubmitPassword,
    formState: { errors: passwordErrors },
    reset: resetPassword,
  } = useForm<PasswordFormData>({
    resolver: yupResolver(passwordSchema),
  })

  if (!user) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          User information not available. Please try refreshing the page.
        </Alert>
      </Box>
    )
  }

  const handleEditToggle = () => {
    if (isEditing) {
      resetProfile({ email: user.email })
    }
    setIsEditing(!isEditing)
  }

  const onSubmitProfile = async (data: ProfileFormData) => {
    setIsLoading(true)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      await axios.put(
        `${API_BASE_URL}/auth/profile`,
        data,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      toast.success('Profile updated successfully!')
      setIsEditing(false)
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to update profile'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const onSubmitPassword = async (data: PasswordFormData) => {
    setIsLoading(true)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      await axios.put(
        `${API_BASE_URL}/auth/change-password`,
        {
          current_password: data.currentPassword,
          new_password: data.newPassword,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      toast.success('Password changed successfully!')
      setPasswordDialogOpen(false)
      resetPassword()
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to change password'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'error'
      case 'instructor':
        return 'warning'
      case 'student':
        return 'primary'
      default:
        return 'default'
    }
  }

  const getInitials = (email: string) => {
    return email.substring(0, 2).toUpperCase()
  }

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        User Profile
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Information Card */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  mr: 3,
                  bgcolor: 'primary.main',
                  fontSize: '1.5rem',
                }}
              >
                {getInitials(user.email)}
              </Avatar>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h5" gutterBottom>
                  {user.email}
                </Typography>
                <Chip
                  label={user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                  color={getRoleColor(user.role) as any}
                  size="small"
                />
              </Box>
              <Button
                variant={isEditing ? 'outlined' : 'contained'}
                startIcon={isEditing ? <Cancel /> : <Edit />}
                onClick={handleEditToggle}
                disabled={isLoading}
              >
                {isEditing ? 'Cancel' : 'Edit'}
              </Button>
            </Box>

            <Divider sx={{ mb: 3 }} />

            <Box component="form" onSubmit={handleSubmitProfile(onSubmitProfile)}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    {...registerProfile('email')}
                    fullWidth
                    label="Email Address"
                    type="email"
                    disabled={!isEditing}
                    error={!!profileErrors.email}
                    helperText={profileErrors.email?.message}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Email color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Role"
                    value={user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                    disabled
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Person color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Member Since"
                    value={format(new Date(user.created_at), 'MMM dd, yyyy')}
                    disabled
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <CalendarToday color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                {user.last_login && (
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Last Login"
                      value={format(new Date(user.last_login), 'MMM dd, yyyy HH:mm')}
                      disabled
                    />
                  </Grid>
                )}

                {isEditing && (
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                      <Button
                        type="submit"
                        variant="contained"
                        startIcon={isLoading ? <CircularProgress size={16} /> : <Save />}
                        disabled={isLoading}
                      >
                        Save Changes
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Box>
          </Paper>
        </Grid>

        {/* Security Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Security
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Keep your account secure by using a strong password.
              </Typography>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Lock />}
                onClick={() => setPasswordDialogOpen(true)}
              >
                Change Password
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Change Password Dialog */}
      <Dialog
        open={passwordDialogOpen}
        onClose={() => setPasswordDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 1 }}>
            <TextField
              {...registerPassword('currentPassword')}
              fullWidth
              label="Current Password"
              type={showCurrentPassword ? 'text' : 'password'}
              margin="normal"
              error={!!passwordErrors.currentPassword}
              helperText={passwordErrors.currentPassword?.message}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      edge="end"
                    >
                      {showCurrentPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              {...registerPassword('newPassword')}
              fullWidth
              label="New Password"
              type={showNewPassword ? 'text' : 'password'}
              margin="normal"
              error={!!passwordErrors.newPassword}
              helperText={passwordErrors.newPassword?.message}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      edge="end"
                    >
                      {showNewPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              {...registerPassword('confirmPassword')}
              fullWidth
              label="Confirm New Password"
              type={showConfirmPassword ? 'text' : 'password'}
              margin="normal"
              error={!!passwordErrors.confirmPassword}
              helperText={passwordErrors.confirmPassword?.message}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      edge="end"
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setPasswordDialogOpen(false)
              resetPassword()
            }}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitPassword(onSubmitPassword)}
            variant="contained"
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={16} /> : null}
          >
            Change Password
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}