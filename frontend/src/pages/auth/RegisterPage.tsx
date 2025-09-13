import React from 'react'
import { Box, Container } from '@mui/material'
import { RegisterForm } from '../../components/auth/RegisterForm'

export const RegisterPage: React.FC = () => {
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
        <RegisterForm />
      </Box>
    </Container>
  )
}