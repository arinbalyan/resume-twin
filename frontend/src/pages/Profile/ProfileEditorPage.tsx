import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

// SVG Icons
const UserIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
)

const BriefcaseIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
  </svg>
)

const GraduationCapIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
    <path d="M6 12v5c3 3 9 3 12 0v-5"/>
  </svg>
)

const ArrowLeftIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/>
    <polyline points="12 19 5 12 12 5"/>
  </svg>
)

const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"/>
    <line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
)

const TrashIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  </svg>
)

export default function ProfileEditorPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'personal' | 'experience' | 'education'>('personal')
  
  const [personalInfo, setPersonalInfo] = useState({
    fullName: '',
    email: user?.email || '',
    phone: '',
    location: '',
    linkedin: '',
    bio: ''
  })

  const [experiences, setExperiences] = useState<any[]>([])
  const [educations, setEducations] = useState<any[]>([])

  const handleSave = () => {
    toast.success('Profile saved successfully!')
  }

  const tabs = [
    { id: 'personal', label: 'Personal Info', icon: <UserIcon /> },
    { id: 'experience', label: 'Experience', icon: <BriefcaseIcon /> },
    { id: 'education', label: 'Education', icon: <GraduationCapIcon /> }
  ]

  const renderPersonalTab = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {[
        { label: 'Full Name', key: 'fullName', placeholder: 'John Doe' },
        { label: 'Email', key: 'email', placeholder: 'john@example.com', type: 'email' },
        { label: 'Phone', key: 'phone', placeholder: '+1 (555) 123-4567' },
        { label: 'Location', key: 'location', placeholder: 'New York, NY' },
        { label: 'LinkedIn', key: 'linkedin', placeholder: 'linkedin.com/in/johndoe' }
      ].map((field) => (
        <div key={field.key}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
            {field.label}
          </label>
          <input
            type={field.type || 'text'}
            value={personalInfo[field.key as keyof typeof personalInfo]}
            onChange={(e) => setPersonalInfo({ ...personalInfo, [field.key]: e.target.value })}
            placeholder={field.placeholder}
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid #e7e5e4',
              fontSize: '15px',
              background: '#fafaf9',
              color: '#1c1917',
              outline: 'none'
            }}
          />
        </div>
      ))}
      <div>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
          Bio
        </label>
        <textarea
          value={personalInfo.bio}
          onChange={(e) => setPersonalInfo({ ...personalInfo, bio: e.target.value })}
          placeholder="Tell us about yourself..."
          rows={4}
          style={{
            width: '100%',
            padding: '12px 16px',
            borderRadius: '8px',
            border: '1px solid #e7e5e4',
            fontSize: '15px',
            background: '#fafaf9',
            color: '#1c1917',
            outline: 'none',
            fontFamily: 'inherit',
            resize: 'vertical'
          }}
        />
      </div>
    </div>
  )

  const renderExperienceTab = () => (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <p style={{ color: '#78716c', fontSize: '14px' }}>
          Add your work experience
        </p>
        <button
          onClick={() => {
            setExperiences([...experiences, { id: Date.now(), company: '', position: '', description: '' }])
            toast.success('Experience added')
          }}
          style={{
            padding: '10px 20px',
            borderRadius: '10px',
            background: '#facc15',
            border: 'none',
            color: '#1e3a8a',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s',
            boxShadow: '0 2px 8px rgba(250, 204, 21, 0.3)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)'
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(250, 204, 21, 0.4)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 2px 8px rgba(250, 204, 21, 0.3)'
          }}
        >
          <PlusIcon /> Add Experience
        </button>
      </div>
      
      {experiences.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', background: '#fafaf9', borderRadius: '12px', border: '1px dashed #e7e5e4' }}>
          <p style={{ color: '#78716c', fontSize: '15px' }}>No experience entries yet</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {experiences.map((exp, idx) => (
            <div key={exp.id} style={{ padding: '20px', background: '#fafaf9', borderRadius: '12px', border: '1px solid #e7e5e4' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917' }}>
                  Experience {idx + 1}
                </h4>
                <button
                  onClick={() => {
                    setExperiences(experiences.filter(e => e.id !== exp.id))
                    toast.success('Experience removed')
                  }}
                  style={{ 
                    color: '#dc2626', 
                    fontSize: '14px', 
                    background: 'none', 
                    border: 'none', 
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#fef2f2'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'none'
                  }}
                >
                  <TrashIcon /> Remove
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <input
                  placeholder="Company"
                  value={exp.company}
                  onChange={(e) => {
                    const updated = [...experiences]
                    updated[idx].company = e.target.value
                    setExperiences(updated)
                  }}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', fontSize: '14px' }}
                />
                <input
                  placeholder="Position"
                  value={exp.position}
                  onChange={(e) => {
                    const updated = [...experiences]
                    updated[idx].position = e.target.value
                    setExperiences(updated)
                  }}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', fontSize: '14px' }}
                />
                <textarea
                  placeholder="Description"
                  value={exp.description}
                  onChange={(e) => {
                    const updated = [...experiences]
                    updated[idx].description = e.target.value
                    setExperiences(updated)
                  }}
                  rows={3}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', fontSize: '14px', fontFamily: 'inherit' }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  const renderEducationTab = () => (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <p style={{ color: '#78716c', fontSize: '14px' }}>
          Add your educational background
        </p>
        <button
          onClick={() => {
            setEducations([...educations, { id: Date.now(), institution: '', degree: '', field: '' }])
            toast.success('Education added')
          }}
          style={{
            padding: '10px 20px',
            borderRadius: '10px',
            background: '#facc15',
            border: 'none',
            color: '#1e3a8a',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s',
            boxShadow: '0 2px 8px rgba(250, 204, 21, 0.3)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)'
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(250, 204, 21, 0.4)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 2px 8px rgba(250, 204, 21, 0.3)'
          }}
        >
          <PlusIcon /> Add Education
        </button>
      </div>
      
      {educations.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', background: '#fafaf9', borderRadius: '12px', border: '1px dashed #e7e5e4' }}>
          <p style={{ color: '#78716c', fontSize: '15px' }}>No education entries yet</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {educations.map((edu, idx) => (
            <div key={edu.id} style={{ padding: '20px', background: '#fafaf9', borderRadius: '12px', border: '1px solid #e7e5e4' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917' }}>
                  Education {idx + 1}
                </h4>
                <button
                  onClick={() => {
                    setEducations(educations.filter(e => e.id !== edu.id))
                    toast.success('Education removed')
                  }}
                  style={{ 
                    color: '#dc2626', 
                    fontSize: '14px', 
                    background: 'none', 
                    border: 'none', 
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#fef2f2'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'none'
                  }}
                >
                  <TrashIcon /> Remove
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <input
                  placeholder="Institution"
                  value={edu.institution}
                  onChange={(e) => {
                    const updated = [...educations]
                    updated[idx].institution = e.target.value
                    setEducations(updated)
                  }}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', fontSize: '14px' }}
                />
                <input
                  placeholder="Degree"
                  value={edu.degree}
                  onChange={(e) => {
                    const updated = [...educations]
                    updated[idx].degree = e.target.value
                    setEducations(updated)
                  }}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', fontSize: '14px' }}
                />
                <input
                  placeholder="Field of Study"
                  value={edu.field}
                  onChange={(e) => {
                    const updated = [...educations]
                    updated[idx].field = e.target.value
                    setEducations(updated)
                  }}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', fontSize: '14px' }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', background: '#fafaf9' }}>
      {/* Header */}
      <div style={{
        background: '#ffffff',
        borderBottom: '1px solid #e7e5e4',
        padding: '20px 32px',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{
                padding: '10px 18px',
                borderRadius: '10px',
                background: 'transparent',
                border: '1px solid #e7e5e4',
                color: '#1c1917',
                cursor: 'pointer',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.2s',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#1e3a8a'
                e.currentTarget.style.background = '#fafaf9'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e7e5e4'
                e.currentTarget.style.background = 'transparent'
              }}
            >
              <ArrowLeftIcon /> Back
            </button>
            <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#1c1917', letterSpacing: '-0.01em' }}>Profile Editor</h1>
          </div>
          <button
            onClick={handleSave}
            style={{
              padding: '10px 24px',
              borderRadius: '8px',
              background: '#facc15',
              border: 'none',
              color: '#1e3a8a',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            Save Changes
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 32px' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '32px', background: '#ffffff', padding: '8px', borderRadius: '14px', border: '1px solid #e7e5e4', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                flex: 1,
                padding: '14px 20px',
                borderRadius: '10px',
                background: activeTab === tab.id ? 'linear-gradient(135deg, #facc15 0%, #fbbf24 100%)' : 'transparent',
                border: 'none',
                color: activeTab === tab.id ? '#1e3a8a' : '#78716c',
                fontWeight: activeTab === tab.id ? '600' : '500',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px',
                boxShadow: activeTab === tab.id ? '0 2px 8px rgba(250, 204, 21, 0.3)' : 'none'
              }}
              onMouseEnter={(e) => {
                if (activeTab !== tab.id) {
                  e.currentTarget.style.background = '#fafaf9'
                  e.currentTarget.style.color = '#1c1917'
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== tab.id) {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = '#78716c'
                }
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '32px',
          border: '1px solid #e7e5e4',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
        }}>
          {activeTab === 'personal' && renderPersonalTab()}
          {activeTab === 'experience' && renderExperienceTab()}
          {activeTab === 'education' && renderEducationTab()}
        </div>
      </div>
    </div>
  )
}
