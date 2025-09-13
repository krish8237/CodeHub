import React from 'react'
import { Box, Container } from '@mui/material'
import { LoginForm } from '../../components/auth/LoginForm'

export const LoginPage: React.FC = () => {
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
        <LoginForm />
      </Box>
    </Container>
  )
}