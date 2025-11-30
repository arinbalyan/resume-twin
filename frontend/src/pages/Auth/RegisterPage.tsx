import React from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { useAuth } from '../../hooks/useAuth'
import LoadingSpinner from '../../components/common/LoadingSpinner'

interface RegisterFormData {
  fullName: string
  email: string
  password: string
  confirmPassword: string
}

const RegisterPage: React.FC = () => {
  const { register: registerUser, loading } = useAuth()
  const navigate = useNavigate()
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>()

  const password = watch('password')

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await registerUser(data.email, data.password, data.fullName)
      toast.success('Account created successfully!')
      navigate('/dashboard')
    } catch (error: any) {
      toast.error(error.message || 'Registration failed. Please try again.')
      console.error('Registration error:', error)
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafaf9' }}>
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafaf9', padding: '20px' }}>
      <div style={{ width: '100%', maxWidth: '440px' }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', marginBottom: '32px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: '#facc15',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '700',
            fontSize: '24px',
            color: '#1e3a8a'
          }}>
            RT
          </div>
          <span style={{ fontSize: '28px', fontWeight: '700', color: '#1c1917' }}>
            Resume Twin
          </span>
        </div>

        {/* Register Card */}
        <div style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '40px',
          border: '1px solid #e7e5e4',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
        }}>
          <div style={{ marginBottom: '32px', textAlign: 'center' }}>
            <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#1c1917', marginBottom: '8px' }}>
              Create Account
            </h2>
            <p style={{ color: '#78716c', fontSize: '15px' }}>
              Already have an account?{' '}
              <Link to="/login" style={{ color: '#1e3a8a', fontWeight: '500', textDecoration: 'none' }}>
                Sign in
              </Link>
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <label htmlFor="fullName" style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                Full Name
              </label>
              <input
                {...register('fullName', {
                  required: 'Full name is required',
                  minLength: { value: 2, message: 'Name must be at least 2 characters' },
                })}
                type="text"
                autoComplete="name"
                placeholder="John Doe"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid #e7e5e4',
                  fontSize: '15px',
                  background: '#fafaf9',
                  color: '#1c1917',
                  outline: 'none',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#facc15'
                  e.currentTarget.style.background = '#ffffff'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#e7e5e4'
                  e.currentTarget.style.background = '#fafaf9'
                }}
              />
              {errors.fullName && (
                <p style={{ marginTop: '6px', fontSize: '13px', color: '#dc2626' }}>{errors.fullName.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                Email Address
              </label>
              <input
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                })}
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid #e7e5e4',
                  fontSize: '15px',
                  background: '#fafaf9',
                  color: '#1c1917',
                  outline: 'none',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#facc15'
                  e.currentTarget.style.background = '#ffffff'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#e7e5e4'
                  e.currentTarget.style.background = '#fafaf9'
                }}
              />
              {errors.email && (
                <p style={{ marginTop: '6px', fontSize: '13px', color: '#dc2626' }}>{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                Password
              </label>
              <input
                {...register('password', {
                  required: 'Password is required',
                  minLength: { value: 8, message: 'Password must be at least 8 characters' },
                })}
                type="password"
                autoComplete="new-password"
                placeholder="Create a strong password"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid #e7e5e4',
                  fontSize: '15px',
                  background: '#fafaf9',
                  color: '#1c1917',
                  outline: 'none',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#facc15'
                  e.currentTarget.style.background = '#ffffff'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#e7e5e4'
                  e.currentTarget.style.background = '#fafaf9'
                }}
              />
              {errors.password && (
                <p style={{ marginTop: '6px', fontSize: '13px', color: '#dc2626' }}>{errors.password.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                Confirm Password
              </label>
              <input
                {...register('confirmPassword', {
                  required: 'Please confirm your password',
                  validate: (value) => value === password || 'Passwords do not match',
                })}
                type="password"
                autoComplete="new-password"
                placeholder="Confirm your password"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid #e7e5e4',
                  fontSize: '15px',
                  background: '#fafaf9',
                  color: '#1c1917',
                  outline: 'none',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#facc15'
                  e.currentTarget.style.background = '#ffffff'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#e7e5e4'
                  e.currentTarget.style.background = '#fafaf9'
                }}
              />
              {errors.confirmPassword && (
                <p style={{ marginTop: '6px', fontSize: '13px', color: '#dc2626' }}>{errors.confirmPassword.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                width: '100%',
                padding: '14px',
                borderRadius: '8px',
                background: isSubmitting ? '#fbbf24' : '#facc15',
                border: 'none',
                color: '#1e3a8a',
                fontWeight: '600',
                fontSize: '15px',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                if (!isSubmitting) {
                  e.currentTarget.style.background = '#fbbf24'
                  e.currentTarget.style.transform = 'translateY(-1px)'
                }
              }}
              onMouseLeave={(e) => {
                if (!isSubmitting) {
                  e.currentTarget.style.background = '#facc15'
                  e.currentTarget.style.transform = 'translateY(0)'
                }
              }}
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="sm" color="#1e3a8a" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>

            <p style={{ fontSize: '12px', textAlign: 'center', color: '#78716c' }}>
              By signing up, you agree to our Terms of Service and Privacy Policy
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage