import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

// SVG Icons
const ArrowLeftIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/>
    <polyline points="12 19 5 12 12 5"/>
  </svg>
)

const CheckIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
)

const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"/>
    <line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
)

interface Template {
  id: string
  name: string
  description: string
}

interface ResumeData {
  personalInfo: {
    fullName: string
    email: string
    phone: string
    location: string
    linkedin: string
  }
  summary: string
  selectedProjects: string[]
  selectedTags: string[]
  experience: Array<{
    company: string
    position: string
    startDate: string
    endDate: string
    description: string
  }>
  education: Array<{
    institution: string
    degree: string
    field: string
    year: string
  }>
  skills: string[]
}

interface Project {
  id: string
  name: string
  description: string
  tags: string[]
  technologies: string[]
}

export default function ResumeBuilderPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [resumeData, setResumeData] = useState<ResumeData>({
    personalInfo: {
      fullName: '',
      email: user?.email || '',
      phone: '',
      location: '',
      linkedin: ''
    },
    summary: '',
    selectedProjects: [],
    selectedTags: [],
    experience: [],
    education: [],
    skills: []
  })

  // Mock projects data - would come from API
  const availableProjects: Project[] = [
    {
      id: '1',
      name: 'E-commerce Platform',
      description: 'Full-stack online shopping platform',
      tags: ['full-stack', 'e-commerce', 'web-dev'],
      technologies: ['React', 'Node.js', 'PostgreSQL']
    },
    {
      id: '2',
      name: 'Machine Learning Model',
      description: 'Predictive analytics system',
      tags: ['machine-learning', 'data-science', 'python'],
      technologies: ['Python', 'TensorFlow', 'Pandas']
    },
    {
      id: '3',
      name: 'Mobile App',
      description: 'Cross-platform mobile application',
      tags: ['mobile', 'cross-platform', 'app-dev'],
      technologies: ['React Native', 'Firebase']
    }
  ]

  const availableTags = Array.from(new Set(availableProjects.flatMap(p => p.tags)))

  const templates: Template[] = [
    { id: '1', name: 'Classic Professional', description: 'Clean and professional design' },
    { id: '2', name: 'Modern Creative', description: 'Bold and modern design' },
    { id: '3', name: 'Tech Minimalist', description: 'Minimalist design for tech roles' },
    { id: '4', name: 'Executive Elite', description: 'Sophisticated design for seniors' }
  ]

  const handleNext = () => {
    if (step === 1 && !selectedTemplate) {
      toast.error('Please select a template')
      return
    }
    if (step < 7) setStep(step + 1)
  }

  const handleBack = () => {
    if (step > 1) setStep(step - 1)
  }

  const handleGenerate = async () => {
    toast.success('Generating your resume...')
    // API call would go here
    setTimeout(() => navigate('/dashboard'), 1500)
  }

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '24px' }}>
              Choose a Template
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
              {templates.map((template) => (
                <div
                  key={template.id}
                  onClick={() => {
                    setSelectedTemplate(template)
                    toast.success(`Template "${template.name}" selected!`)
                  }}
                  style={{
                    background: selectedTemplate?.id === template.id ? '#facc1510' : '#ffffff',
                    border: selectedTemplate?.id === template.id ? '2px solid #facc15' : '1px solid #e7e5e4',
                    borderRadius: '12px',
                    padding: '24px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedTemplate?.id !== template.id) {
                      e.currentTarget.style.borderColor = '#facc15'
                      e.currentTarget.style.transform = 'translateY(-2px)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedTemplate?.id !== template.id) {
                      e.currentTarget.style.borderColor = '#e7e5e4'
                      e.currentTarget.style.transform = 'translateY(0)'
                    }
                  }}
                >
                  <h4 style={{ fontSize: '18px', fontWeight: '600', color: '#1c1917', marginBottom: '8px' }}>
                    {template.name}
                  </h4>
                  <p style={{ fontSize: '14px', color: '#78716c' }}>{template.description}</p>
                </div>
              ))}
            </div>
          </div>
        )

      case 2:
        return (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '24px' }}>
              Personal Information
            </h3>
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
                    value={resumeData.personalInfo[field.key as keyof typeof resumeData.personalInfo]}
                    onChange={(e) => setResumeData({
                      ...resumeData,
                      personalInfo: { ...resumeData.personalInfo, [field.key]: e.target.value }
                    })}
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
            </div>
          </div>
        )

      case 3:
        return (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '24px' }}>
              Professional Summary
            </h3>
            <textarea
              value={resumeData.summary}
              onChange={(e) => setResumeData({ ...resumeData, summary: e.target.value })}
              placeholder="Write a brief summary of your professional background and key achievements..."
              rows={6}
              style={{
                width: '100%',
                padding: '16px',
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
        )

      case 4:
        return (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '16px' }}>
              Select Projects
            </h3>
            <p style={{ fontSize: '14px', color: '#78716c', marginBottom: '24px' }}>
              Choose which projects to include in your resume. You can filter by tags or select individual projects.
            </p>

            {/* Tag Filter */}
            <div style={{ marginBottom: '24px', padding: '20px', background: '#fafaf9', borderRadius: '12px', border: '1px solid #e7e5e4' }}>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '12px' }}>
                Filter by Tags
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {availableTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => {
                      const newTags = resumeData.selectedTags.includes(tag)
                        ? resumeData.selectedTags.filter(t => t !== tag)
                        : [...resumeData.selectedTags, tag]
                      setResumeData({ ...resumeData, selectedTags: newTags })
                    }}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '8px',
                      background: resumeData.selectedTags.includes(tag) ? '#facc15' : '#ffffff',
                      border: resumeData.selectedTags.includes(tag) ? '2px solid #facc15' : '1px solid #e7e5e4',
                      color: resumeData.selectedTags.includes(tag) ? '#1e3a8a' : '#1c1917',
                      fontWeight: resumeData.selectedTags.includes(tag) ? '600' : '500',
                      cursor: 'pointer',
                      fontSize: '14px',
                      transition: 'all 0.2s'
                    }}
                  >
                    #{tag}
                  </button>
                ))}
              </div>
              {resumeData.selectedTags.length > 0 && (
                <p style={{ fontSize: '13px', color: '#78716c', marginTop: '12px' }}>
                  Selected tags: {resumeData.selectedTags.join(', ')}
                </p>
              )}
            </div>

            {/* Project List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {availableProjects
                .filter(project => 
                  resumeData.selectedTags.length === 0 || 
                  resumeData.selectedTags.some(tag => project.tags.includes(tag))
                )
                .map((project) => (
                  <div
                    key={project.id}
                    onClick={() => {
                      const newProjects = resumeData.selectedProjects.includes(project.id)
                        ? resumeData.selectedProjects.filter(p => p !== project.id)
                        : [...resumeData.selectedProjects, project.id]
                      setResumeData({ ...resumeData, selectedProjects: newProjects })
                    }}
                    style={{
                      padding: '20px',
                      background: resumeData.selectedProjects.includes(project.id) ? '#facc1510' : '#ffffff',
                      borderRadius: '12px',
                      border: resumeData.selectedProjects.includes(project.id) ? '2px solid #facc15' : '1px solid #e7e5e4',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      if (!resumeData.selectedProjects.includes(project.id)) {
                        e.currentTarget.style.borderColor = '#facc15'
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!resumeData.selectedProjects.includes(project.id)) {
                        e.currentTarget.style.borderColor = '#e7e5e4'
                      }
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                      <div>
                        <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '4px' }}>
                          {project.name}
                        </h4>
                        <p style={{ fontSize: '14px', color: '#78716c' }}>
                          {project.description}
                        </p>
                      </div>
                      {resumeData.selectedProjects.includes(project.id) && (
                        <span style={{
                          padding: '4px 12px',
                          borderRadius: '12px',
                          background: '#22c55e',
                          color: '#ffffff',
                          fontSize: '12px',
                          fontWeight: '600',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}>
                          <CheckIcon /> Selected
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                      {project.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: '4px 10px',
                            background: '#facc15',
                            borderRadius: '6px',
                            fontSize: '12px',
                            color: '#1e3a8a',
                            fontWeight: '500'
                          }}
                        >
                          #{tag}
                        </span>
                      ))}
                      {project.technologies.map((tech, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: '4px 10px',
                            background: '#fafaf9',
                            border: '1px solid #e7e5e4',
                            borderRadius: '6px',
                            fontSize: '12px',
                            color: '#1c1917'
                          }}
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
            {resumeData.selectedProjects.length > 0 && (
              <p style={{ fontSize: '14px', color: '#22c55e', fontWeight: '600', marginTop: '16px' }}>
                {resumeData.selectedProjects.length} project(s) selected
              </p>
            )}
          </div>
        )

      case 5:
        return (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '16px' }}>
              Work Experience
            </h3>
            <p style={{ fontSize: '14px', color: '#78716c', marginBottom: '24px' }}>
              Add your work experience (click to add new entries)
            </p>
            <button
              onClick={() => {
                setResumeData({
                  ...resumeData,
                  experience: [...resumeData.experience, { company: '', position: '', startDate: '', endDate: '', description: '' }]
                })
              }}
              style={{
                padding: '12px 24px',
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
            {resumeData.experience.length > 0 && (
              <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {resumeData.experience.map((exp, idx) => (
                  <div key={idx} style={{ padding: '20px', background: '#fafaf9', borderRadius: '8px', border: '1px solid #e7e5e4' }}>
                    <input
                      placeholder="Company Name"
                      value={exp.company}
                      onChange={(e) => {
                        const newExp = [...resumeData.experience]
                        newExp[idx].company = e.target.value
                        setResumeData({ ...resumeData, experience: newExp })
                      }}
                      style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', marginBottom: '10px' }}
                    />
                    <input
                      placeholder="Position"
                      value={exp.position}
                      onChange={(e) => {
                        const newExp = [...resumeData.experience]
                        newExp[idx].position = e.target.value
                        setResumeData({ ...resumeData, experience: newExp })
                      }}
                      style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4' }}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        )

      case 6:
        return (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '16px' }}>
              Education
            </h3>
            <p style={{ fontSize: '14px', color: '#78716c', marginBottom: '24px' }}>
              Add your educational background
            </p>
            <button
              onClick={() => {
                setResumeData({
                  ...resumeData,
                  education: [...resumeData.education, { institution: '', degree: '', field: '', year: '' }]
                })
              }}
              style={{
                padding: '12px 24px',
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
            {resumeData.education.length > 0 && (
              <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {resumeData.education.map((edu, idx) => (
                  <div key={idx} style={{ padding: '20px', background: '#fafaf9', borderRadius: '8px', border: '1px solid #e7e5e4' }}>
                    <input
                      placeholder="Institution"
                      value={edu.institution}
                      onChange={(e) => {
                        const newEdu = [...resumeData.education]
                        newEdu[idx].institution = e.target.value
                        setResumeData({ ...resumeData, education: newEdu })
                      }}
                      style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4', marginBottom: '10px' }}
                    />
                    <input
                      placeholder="Degree"
                      value={edu.degree}
                      onChange={(e) => {
                        const newEdu = [...resumeData.education]
                        newEdu[idx].degree = e.target.value
                        setResumeData({ ...resumeData, education: newEdu })
                      }}
                      style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #e7e5e4' }}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        )

      case 7:
        return (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1c1917', marginBottom: '24px' }}>
              Review & Generate
            </h3>
            <div style={{ background: '#fafaf9', padding: '24px', borderRadius: '12px', border: '1px solid #e7e5e4' }}>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '12px' }}>
                Selected Template
              </h4>
              <p style={{ color: '#78716c', marginBottom: '24px' }}>{selectedTemplate?.name}</p>
              
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '12px' }}>
                Personal Info
              </h4>
              <p style={{ color: '#78716c', marginBottom: '8px' }}>{resumeData.personalInfo.fullName || 'Not provided'}</p>
              <p style={{ color: '#78716c', marginBottom: '24px' }}>{resumeData.personalInfo.email || 'Not provided'}</p>
              
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '12px' }}>
                Summary
              </h4>
              <p style={{ color: '#78716c', marginBottom: '24px' }}>
                {resumeData.summary || 'No summary provided'}
              </p>
              
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '12px' }}>
                Selected Projects
              </h4>
              <p style={{ color: '#78716c', marginBottom: '8px' }}>
                {resumeData.selectedProjects.length} project(s) selected
              </p>
              {resumeData.selectedTags.length > 0 && (
                <p style={{ color: '#78716c', marginBottom: '24px' }}>
                  Filtered by tags: {resumeData.selectedTags.join(', ')}
                </p>
              )}
              
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '12px' }}>
                Experience Entries
              </h4>
              <p style={{ color: '#78716c', marginBottom: '24px' }}>
                {resumeData.experience.length} entries
              </p>
              
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1c1917', marginBottom: '12px' }}>
                Education Entries
              </h4>
              <p style={{ color: '#78716c' }}>
                {resumeData.education.length} entries
              </p>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#fafaf9' }}>
      {/* Header */}
      <div style={{
        background: '#ffffff',
        borderBottom: '1px solid #e7e5e4',
        padding: '20px 32px',
        position: 'sticky',
        top: 0,
        zIndex: 50
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
            <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#1c1917' }}>Resume Builder</h1>
          </div>
          <div style={{ fontSize: '14px', color: '#78716c' }}>
            Step {step} of 7
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ background: '#ffffff', borderBottom: '1px solid #e7e5e4', padding: '0 32px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'flex', gap: '8px', paddingBottom: '16px' }}>
            {[1, 2, 3, 4, 5, 6, 7].map((s) => (
              <div
                key={s}
                style={{
                  flex: 1,
                  height: '4px',
                  background: s <= step ? '#facc15' : '#e7e5e4',
                  borderRadius: '2px',
                  transition: 'all 0.3s'
                }}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 32px' }}>
        <div style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '40px',
          border: '1px solid #e7e5e4',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          minHeight: '400px'
        }}>
          {renderStep()}
        </div>

        {/* Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
          <button
            onClick={handleBack}
            disabled={step === 1}
            style={{
              padding: '12px 32px',
              borderRadius: '8px',
              background: 'transparent',
              border: '1px solid #e7e5e4',
              color: step === 1 ? '#78716c' : '#1c1917',
              fontWeight: '500',
              cursor: step === 1 ? 'not-allowed' : 'pointer',
              fontSize: '15px'
            }}
          >
            Back
          </button>
          {step === 7 ? (
            <button
              onClick={handleGenerate}
              style={{
                padding: '12px 32px',
                borderRadius: '8px',
                background: '#facc15',
                border: 'none',
                color: '#1e3a8a',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '15px'
              }}
            >
              Generate Resume
            </button>
          ) : (
            <button
              onClick={handleNext}
              style={{
                padding: '12px 32px',
                borderRadius: '8px',
                background: '#facc15',
                border: 'none',
                color: '#1e3a8a',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '15px'
              }}
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
