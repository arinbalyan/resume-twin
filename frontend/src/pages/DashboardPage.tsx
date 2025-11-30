import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

// SVG Icons
const DocumentIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
  </svg>
)

const BriefcaseIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
  </svg>
)

const LayoutIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
    <line x1="3" y1="9" x2="21" y2="9"/>
    <line x1="9" y1="21" x2="9" y2="9"/>
  </svg>
)

const UserIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
)

const SparklesIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l1.912 5.813a2 2 0 001.272 1.272L21 12l-5.813 1.912a2 2 0 00-1.272 1.272L12 21l-1.912-5.813a2 2 0 00-1.272-1.272L3 12l5.813-1.912a2 2 0 001.272-1.272L12 3z"/>
  </svg>
)

const RocketIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
    <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
  </svg>
)

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  const handleCreateResume = () => {
    navigate('/resume/builder')
  }

  const handleAddProject = () => {
    navigate('/projects')
  }

  const handleEditProfile = () => {
    navigate('/profile')
  }

  return (
    <div style={{ minHeight: '100vh', background: '#fafaf9' }}>
      {/* Header */}
      <header style={{ 
        background: '#ffffff',
        borderBottom: '1px solid #e7e5e4',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '16px 32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                background: '#facc15',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold',
                fontSize: '18px',
                color: '#1e3a8a'
              }}>
                RT
              </div>
              <span style={{ color: '#1c1917', fontWeight: '600', fontSize: '20px' }}>Dashboard</span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <span style={{ color: '#78716c', fontSize: '14px' }}>{user?.email}</span>
              <button
                onClick={handleSignOut}
                style={{
                  padding: '8px 20px',
                  borderRadius: '8px',
                  color: '#1e3a8a',
                  fontWeight: '500',
                  background: 'transparent',
                  border: '1px solid #e7e5e4',
                  cursor: 'pointer',
                  fontSize: '14px',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#fafaf9'
                  e.currentTarget.style.borderColor = '#1e3a8a'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.borderColor = '#e7e5e4'
                }}
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1280px', margin: '0 auto', padding: '48px 32px' }}>
        <div style={{ marginBottom: '48px' }}>
          <h1 style={{ 
            fontSize: '36px', 
            fontWeight: '700', 
            marginBottom: '8px',
            color: '#1c1917',
            letterSpacing: '-0.02em'
          }}>
            Welcome Back
          </h1>
          <p style={{ fontSize: '16px', color: '#78716c' }}>
            Start building your next resume
          </p>
        </div>

        {/* Quick Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px', marginBottom: '56px' }}>
          {[
            { label: 'Resumes', value: '0', color: '#facc15', icon: <DocumentIcon /> },
            { label: 'Projects', value: '0', color: '#fb923c', icon: <BriefcaseIcon /> },
            { label: 'Templates', value: '4', color: '#1e3a8a', icon: <LayoutIcon /> },
            { label: 'Profile', value: '60%', color: '#22c55e', icon: <UserIcon /> },
          ].map((stat, index) => (
            <div
              key={index}
              style={{
                background: '#ffffff',
                borderRadius: '16px',
                padding: '28px',
                border: '1px solid #e7e5e4',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.08)'
                e.currentTarget.style.borderColor = stat.color
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
                e.currentTarget.style.borderColor = '#e7e5e4'
              }}
            >
              <div style={{ 
                width: '48px', 
                height: '48px', 
                background: `linear-gradient(135deg, ${stat.color}20 0%, ${stat.color}10 100%)`,
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: stat.color,
                marginBottom: '16px'
              }}>
                {stat.icon}
              </div>
              <div style={{ fontSize: '32px', fontWeight: '800', color: stat.color, marginBottom: '4px', letterSpacing: '-0.02em' }}>{stat.value}</div>
              <div style={{ color: '#78716c', fontSize: '14px', fontWeight: '500', letterSpacing: '0.01em' }}>{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: '700', color: '#1c1917', marginBottom: '24px', letterSpacing: '-0.01em' }}>
            Quick Actions
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            {[
              {
                title: 'Create Resume',
                description: 'Build a professional resume with AI assistance',
                icon: <SparklesIcon />,
                color: '#facc15',
                action: handleCreateResume,
              },
              {
                title: 'Add Project',
                description: 'Showcase your work and key achievements',
                icon: <RocketIcon />,
                color: '#fb923c',
                action: handleAddProject,
              },
              {
                title: 'Edit Profile',
                description: 'Keep your information up to date',
                icon: <UserIcon />,
                color: '#1e3a8a',
                action: handleEditProfile,
              },
            ].map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                style={{
                  textAlign: 'left',
                  background: '#ffffff',
                  borderRadius: '20px',
                  padding: '32px',
                  border: '1px solid #e7e5e4',
                  cursor: 'pointer',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-6px)'
                  e.currentTarget.style.boxShadow = '0 16px 32px rgba(0,0,0,0.1)'
                  e.currentTarget.style.borderColor = action.color
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = 'none'
                  e.currentTarget.style.borderColor = '#e7e5e4'
                }}
              >
                <div style={{
                  width: '56px',
                  height: '56px',
                  background: `linear-gradient(135deg, ${action.color}20 0%, ${action.color}10 100%)`,
                  borderRadius: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: action.color
                }}>
                  {action.icon}
                </div>
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#1c1917', marginBottom: '6px', letterSpacing: '-0.01em' }}>
                    {action.title}
                  </h3>
                  <p style={{ color: '#78716c', fontSize: '14px', lineHeight: '1.5' }}>
                    {action.description}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

