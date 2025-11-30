import { useNavigate } from 'react-router-dom'

// SVG Icons as components
const SparklesIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l1.912 5.813a2 2 0 001.272 1.272L21 12l-5.813 1.912a2 2 0 00-1.272 1.272L12 21l-1.912-5.813a2 2 0 00-1.272-1.272L3 12l5.813-1.912a2 2 0 001.272-1.272L12 3z"/>
  </svg>
)

const DocumentIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>
)

const CpuIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
    <rect x="9" y="9" width="6" height="6"/>
    <line x1="9" y1="1" x2="9" y2="4"/>
    <line x1="15" y1="1" x2="15" y2="4"/>
    <line x1="9" y1="20" x2="9" y2="23"/>
    <line x1="15" y1="20" x2="15" y2="23"/>
    <line x1="20" y1="9" x2="23" y2="9"/>
    <line x1="20" y1="14" x2="23" y2="14"/>
    <line x1="1" y1="9" x2="4" y2="9"/>
    <line x1="1" y1="14" x2="4" y2="14"/>
  </svg>
)

const ZapIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
  </svg>
)

const CheckIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
)

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
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 18px',
            background: 'linear-gradient(135deg, #facc1515 0%, #fb923c15 100%)',
            borderRadius: '24px',
            marginBottom: '28px',
            border: '1px solid #facc1540',
            boxShadow: '0 2px 8px rgba(250, 204, 21, 0.1)'
          }}>
            <span style={{ color: '#facc15' }}><SparklesIcon /></span>
            <span style={{ color: '#1e3a8a', fontSize: '14px', fontWeight: '600', letterSpacing: '0.02em' }}>
              AI-Powered Resume Builder
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
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '28px',
          marginTop: '80px'
        }}>
          {[
            { icon: <DocumentIcon />, title: 'Smart Templates', desc: 'Choose from professionally designed templates that highlight your strengths', color: '#facc15' },
            { icon: <CpuIcon />, title: 'AI Optimization', desc: 'Automatically tailor your resume to match job descriptions perfectly', color: '#fb923c' },
            { icon: <ZapIcon />, title: 'Quick Export', desc: 'Download your polished resume as PDF in just seconds', color: '#1e3a8a' },
          ].map((feature, index) => (
            <div
              key={index}
              style={{
                background: '#ffffff',
                borderRadius: '20px',
                padding: '36px',
                border: '1px solid #e7e5e4',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-6px)'
                e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)'
                e.currentTarget.style.borderColor = feature.color
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
                e.currentTarget.style.borderColor = '#e7e5e4'
              }}
            >
              <div style={{
                width: '60px',
                height: '60px',
                background: `linear-gradient(135deg, ${feature.color}20 0%, ${feature.color}10 100%)`,
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '24px',
                color: feature.color
              }}>
                {feature.icon}
              </div>
              <h3 style={{ fontSize: '20px', fontWeight: '700', color: '#1c1917', marginBottom: '10px', letterSpacing: '-0.01em' }}>
                {feature.title}
              </h3>
              <p style={{ color: '#78716c', fontSize: '15px', lineHeight: '1.6' }}>
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

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px' }}>
            {[
              { title: 'ATS-Friendly', desc: 'Optimized for Applicant Tracking Systems to maximize your visibility', color: '#facc15' },
              { title: 'Multiple Formats', desc: 'Export as PDF, Word, or plain text for any application', color: '#fb923c' },
              { title: 'Live Preview', desc: 'See changes in real-time as you build your resume', color: '#1e3a8a' },
              { title: 'Custom Sections', desc: 'Add projects, certifications, skills, and more', color: '#22c55e' },
            ].map((item, index) => (
              <div key={index} style={{ 
                display: 'flex', 
                gap: '20px', 
                alignItems: 'flex-start',
                padding: '24px',
                background: '#fafaf9',
                borderRadius: '16px',
                border: '1px solid #e7e5e4',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = item.color
                e.currentTarget.style.background = '#ffffff'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e7e5e4'
                e.currentTarget.style.background = '#fafaf9'
              }}
              >
                <div style={{
                  width: '48px',
                  height: '48px',
                  background: `linear-gradient(135deg, ${item.color}25 0%, ${item.color}15 100%)`,
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: item.color,
                  flexShrink: 0
                }}>
                  <CheckIcon />
                </div>
                <div>
                  <h4 style={{ fontSize: '18px', fontWeight: '700', color: '#1c1917', marginBottom: '6px' }}>
                    {item.title}
                  </h4>
                  <p style={{ color: '#78716c', fontSize: '14px', lineHeight: '1.6' }}>
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
      <footer style={{ background: '#ffffff', borderTop: '1px solid #e7e5e4', padding: '48px 32px' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                background: '#facc15',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '700',
                fontSize: '14px',
                color: '#1e3a8a'
              }}>
                RT
              </div>
              <span style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917' }}>
                Resume Twin
              </span>
            </div>
            <p style={{ color: '#78716c', fontSize: '14px' }}>
              © 2025 Resume Twin. Crafted for ambitious professionals.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
