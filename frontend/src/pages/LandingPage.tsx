import { useNavigate } from 'react-router-dom'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div style={{ minHeight: '100vh', background: '#fafaf9' }}>
      {/* Navigation */}
      <nav style={{
        background: '#ffffff',
        borderBottom: '1px solid #e7e5e4',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '20px 32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: '#facc15',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '700',
                fontSize: '20px',
                color: '#1e3a8a'
              }}>
                RT
              </div>
              <span style={{ fontSize: '24px', fontWeight: '700', color: '#1c1917' }}>
                Resume Twin
              </span>
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => navigate('/login')}
                style={{
                  padding: '10px 24px',
                  borderRadius: '8px',
                  background: 'transparent',
                  border: '1px solid #e7e5e4',
                  color: '#1c1917',
                  fontWeight: '500',
                  cursor: 'pointer',
                  fontSize: '15px',
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
                Sign In
              </button>
              <button
                onClick={() => navigate('/register')}
                style={{
                  padding: '10px 24px',
                  borderRadius: '8px',
                  background: '#facc15',
                  border: 'none',
                  color: '#1e3a8a',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '15px',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#fbbf24'
                  e.currentTarget.style.transform = 'translateY(-1px)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#facc15'
                  e.currentTarget.style.transform = 'translateY(0)'
                }}
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{ maxWidth: '1280px', margin: '0 auto', padding: '80px 32px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            display: 'inline-block',
            padding: '6px 16px',
            background: '#facc1520',
            borderRadius: '20px',
            marginBottom: '24px',
            border: '1px solid #facc1540'
          }}>
            <span style={{ color: '#1e3a8a', fontSize: '14px', fontWeight: '600' }}>
              ✨ AI-Powered Resume Builder
            </span>
          </div>
          
          <h1 style={{
            fontSize: '64px',
            fontWeight: '800',
            color: '#1c1917',
            marginBottom: '24px',
            lineHeight: '1.1',
            letterSpacing: '-0.03em'
          }}>
            Build Your Perfect
            <br />
            <span style={{ color: '#facc15' }}>Resume</span> in Minutes
          </h1>
          
          <p style={{
            fontSize: '20px',
            color: '#78716c',
            marginBottom: '40px',
            lineHeight: '1.6'
          }}>
            Create professional, ATS-friendly resumes tailored to your dream job.
            <br />
            No design skills required.
          </p>
          
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate('/register')}
              style={{
                padding: '16px 40px',
                borderRadius: '12px',
                background: '#facc15',
                border: 'none',
                color: '#1e3a8a',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '16px',
                transition: 'all 0.2s',
                boxShadow: '0 4px 12px rgba(250, 204, 21, 0.3)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 8px 20px rgba(250, 204, 21, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(250, 204, 21, 0.3)'
              }}
            >
              Start Building Free
            </button>
            <button
              style={{
                padding: '16px 40px',
                borderRadius: '12px',
                background: 'transparent',
                border: '1px solid #e7e5e4',
                color: '#1c1917',
                fontWeight: '500',
                cursor: 'pointer',
                fontSize: '16px',
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
              View Templates
            </button>
          </div>
        </div>

        {/* Preview Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
          marginTop: '80px'
        }}>
          {[
            { icon: '📝', title: 'Smart Templates', desc: 'Choose from professional templates', color: '#facc15' },
            { icon: '🤖', title: 'AI Optimization', desc: 'Match job descriptions perfectly', color: '#fb923c' },
            { icon: '⚡', title: 'Quick Export', desc: 'Download PDF in seconds', color: '#1e3a8a' },
          ].map((feature, index) => (
            <div
              key={index}
              style={{
                background: '#ffffff',
                borderRadius: '16px',
                padding: '32px',
                border: '1px solid #e7e5e4',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(0,0,0,0.08)'
                e.currentTarget.style.borderColor = feature.color
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
                background: feature.color + '20',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
                marginBottom: '20px'
              }}>
                {feature.icon}
              </div>
              <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '8px' }}>
                {feature.title}
              </h3>
              <p style={{ color: '#78716c', fontSize: '15px', lineHeight: '1.5' }}>
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section style={{ background: '#ffffff', borderTop: '1px solid #e7e5e4', padding: '80px 32px' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '60px' }}>
            <h2 style={{ fontSize: '42px', fontWeight: '700', color: '#1c1917', marginBottom: '16px' }}>
              Everything You Need
            </h2>
            <p style={{ fontSize: '18px', color: '#78716c' }}>
              Professional tools to create standout resumes
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '40px' }}>
            {[
              { title: 'ATS-Friendly', desc: 'Optimized for Applicant Tracking Systems', icon: '✓', color: '#facc15' },
              { title: 'Multiple Formats', desc: 'Export as PDF, Word, or plain text', icon: '✓', color: '#fb923c' },
              { title: 'Live Preview', desc: 'See changes in real-time', icon: '✓', color: '#1e3a8a' },
              { title: 'Custom Sections', desc: 'Add projects, skills, and more', icon: '✓', color: '#78716c' },
            ].map((item, index) => (
              <div key={index} style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  background: item.color + '20',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '24px',
                  fontWeight: '700',
                  color: item.color,
                  flexShrink: 0
                }}>
                  {item.icon}
                </div>
                <div>
                  <h4 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '8px' }}>
                    {item.title}
                  </h4>
                  <p style={{ color: '#78716c', fontSize: '15px', lineHeight: '1.6' }}>
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section style={{ maxWidth: '1280px', margin: '0 auto', padding: '80px 32px' }}>
        <div style={{
          background: '#facc15',
          borderRadius: '24px',
          padding: '60px',
          textAlign: 'center'
        }}>
          <h2 style={{ fontSize: '42px', fontWeight: '700', color: '#1e3a8a', marginBottom: '16px' }}>
            Ready to Build Your Resume?
          </h2>
          <p style={{ fontSize: '18px', color: '#78716c', marginBottom: '32px' }}>
            Join thousands of job seekers who landed their dream jobs
          </p>
          <button
            onClick={() => navigate('/register')}
            style={{
              padding: '16px 48px',
              borderRadius: '12px',
              background: '#1e3a8a',
              border: 'none',
              color: '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '16px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 8px 20px rgba(30, 58, 138, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            Get Started for Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ background: '#ffffff', borderTop: '1px solid #e7e5e4', padding: '40px 32px' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', textAlign: 'center' }}>
          <p style={{ color: '#78716c', fontSize: '14px' }}>
            © 2025 Resume Twin. Built with ❤️ for job seekers.
          </p>
        </div>
      </footer>
    </div>
  )
}
