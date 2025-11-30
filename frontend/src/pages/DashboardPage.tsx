import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

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
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '48px' }}>
          {[
            { label: 'Resumes', value: '0', color: '#facc15', icon: '📄' },
            { label: 'Projects', value: '0', color: '#fb923c', icon: '💼' },
            { label: 'Templates', value: '4', color: '#1e3a8a', icon: '🎨' },
            { label: 'Profile', value: '60%', color: '#78716c', icon: '👤' },
          ].map((stat, index) => (
            <div
              key={index}
              style={{
                background: '#ffffff',
                borderRadius: '12px',
                padding: '24px',
                border: '1px solid #e7e5e4',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>{stat.icon}</div>
              <div style={{ fontSize: '28px', fontWeight: '700', color: stat.color, marginBottom: '4px' }}>{stat.value}</div>
              <div style={{ color: '#78716c', fontSize: '14px', fontWeight: '500' }}>{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '20px' }}>
            Quick Actions
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            {[
              {
                title: 'Create Resume',
                description: 'Build a professional resume with AI',
                icon: '✨',
                color: '#facc15',
                action: handleCreateResume,
              },
              {
                title: 'Add Project',
                description: 'Showcase your work and achievements',
                icon: '🚀',
                color: '#fb923c',
                action: handleAddProject,
              },
              {
                title: 'Edit Profile',
                description: 'Update your information',
                icon: '👤',
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
                  borderRadius: '16px',
                  padding: '28px',
                  border: '1px solid #e7e5e4',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)'
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.08)'
                  e.currentTarget.style.borderColor = action.color
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
                  background: action.color + '20',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '24px'
                }}>
                  {action.icon}
                </div>
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1c1917', marginBottom: '4px' }}>
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

