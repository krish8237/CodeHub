import { configureStore } from '@reduxjs/toolkit'

// Reducers will be added in later tasks
// import authReducer from './slices/authSlice'
// import assessmentReducer from './slices/assessmentSlice'
// import uiReducer from './slices/uiSlice'

export const store = configureStore({
  reducer: {
    // auth: authReducer,
    // assessment: assessmentReducer,
    // ui: uiReducer,
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