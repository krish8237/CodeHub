import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import uiReducer from './slices/uiSlice'

// Assessment reducer will be added in later tasks
// import assessmentReducer from './slices/assessmentSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    ui: uiReducer,
    // assessment: assessmentReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch