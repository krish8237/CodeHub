import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import axios from 'axios'

// Types
export interface User {
  id: number
  email: string
  role: 'student' | 'instructor' | 'admin'
  created_at: string
  last_login?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  confirmPassword: string
  role?: 'student' | 'instructor'
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
}

// Initial state
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, credentials)
      const data: AuthResponse = response.data
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      return data
    } catch (error: any) {
      const message = error.response?.data?.message || 'Login failed'
      return rejectWithValue(message)
    }
  }
)

export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData: RegisterData, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, userData)
      return response.data
    } catch (error: any) {
      const message = error.response?.data?.message || 'Registration failed'
      return rejectWithValue(message)
    }
  }
)

export const refreshToken = createAsyncThunk(
  'auth/refresh',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState }
      const refreshToken = state.auth.refreshToken
      
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }
      
      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken
      })
      
      const data: AuthResponse = response.data
      
      // Update tokens in localStorage
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      return data
    } catch (error: any) {
      const message = error.response?.data?.message || 'Token refresh failed'
      return rejectWithValue(message)
    }
  }
)

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState }
      const token = state.auth.token
      
      if (!token) {
        throw new Error('No token available')
      }
      
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      return response.data
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to get user info'
      return rejectWithValue(message)
    }
  }
)

export const requestPasswordReset = createAsyncThunk(
  'auth/requestPasswordReset',
  async (email: string, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/password-reset-request`, {
        email
      })
      return response.data
    } catch (error: any) {
      const message = error.response?.data?.message || 'Password reset request failed'
      return rejectWithValue(message)
    }
  }
)

export const resetPassword = createAsyncThunk(
  'auth/resetPassword',
  async ({ token, password }: { token: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/password-reset`, {
        token,
        password
      })
      return response.data
    } catch (error: any) {
      const message = error.response?.data?.message || 'Password reset failed'
      return rejectWithValue(message)
    }
  }
)

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = null
      
      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
    clearError: (state) => {
      state.error = null
    },
    setCredentials: (state, action: PayloadAction<AuthResponse>) => {
      state.user = action.payload.user
      state.token = action.payload.access_token
      state.refreshToken = action.payload.refresh_token
      state.isAuthenticated = true
      state.error = null
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false
        state.user = action.payload.user
        state.token = action.payload.access_token
        state.refreshToken = action.payload.refresh_token
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
        state.isAuthenticated = false
      })
    
    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.isLoading = false
        state.error = null
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
    
    // Refresh token
    builder
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.user = action.payload.user
        state.token = action.payload.access_token
        state.refreshToken = action.payload.refresh_token
        state.isAuthenticated = true
      })
      .addCase(refreshToken.rejected, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      })
    
    // Get current user
    builder
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload
        state.isAuthenticated = true
      })
      .addCase(getCurrentUser.rejected, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      })
    
    // Password reset request
    builder
      .addCase(requestPasswordReset.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(requestPasswordReset.fulfilled, (state) => {
        state.isLoading = false
        state.error = null
      })
      .addCase(requestPasswordReset.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
    
    // Password reset
    builder
      .addCase(resetPassword.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(resetPassword.fulfilled, (state) => {
        state.isLoading = false
        state.error = null
      })
      .addCase(resetPassword.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
  },
})

export const { logout, clearError, setCredentials } = authSlice.actions
export default authSlice.reducer