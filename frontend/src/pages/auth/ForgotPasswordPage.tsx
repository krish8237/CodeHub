import React from 'react'
import { Box, Container } from '@mui/material'
import { ForgotPasswordForm } from '../../components/auth/ForgotPasswordForm'

export const ForgotPasswordPage: React.FC = () => {
  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <ForgotPasswordForm />
      </Box>
    </Container>
  )
}