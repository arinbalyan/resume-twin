import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

interface Project {
  id: number
  name: string
  description: string
  bulletPoints: string[]
  tags: string[]
  status: 'active' | 'completed' | 'archived'
  technologies: string[]
  link?: string
}

export default function ProjectsManagerPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([
    {
      id: 1,
      name: 'E-commerce Platform',
      description: 'Full-stack online shopping platform with payment integration',
      bulletPoints: [
        'Implemented user authentication and authorization system',
        'Integrated Stripe payment gateway for secure transactions',
        'Built responsive product catalog with advanced filtering'
      ],
      tags: ['full-stack', 'e-commerce', 'payment-integration'],
      status: 'active',
      technologies: ['React', 'Node.js', 'PostgreSQL'],
      link: 'https://github.com/example/ecommerce'
    },
    {
      id: 2,
      name: 'Task Management App',
      description: 'Collaborative task tracking application',
      bulletPoints: [
        'Developed real-time collaboration features using WebSockets',
        'Implemented drag-and-drop task prioritization',
        'Created custom notification system'
      ],
      tags: ['web-app', 'collaboration', 'real-time'],
      status: 'completed',
      technologies: ['Vue.js', 'Firebase'],
      link: 'https://github.com/example/taskapp'
    }
  ])
  
  const [showModal, setShowModal] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    bulletPoints: '',
    tags: '',
    status: 'active' as Project['status'],
    technologies: '',
    link: ''
  })

  const handleAddProject = () => {
    setEditingProject(null)
    setFormData({ name: '', description: '', bulletPoints: '', tags: '', status: 'active', technologies: '', link: '' })
    setShowModal(true)
  }

  const handleEditProject = (project: Project) => {
    setEditingProject(project)
    setFormData({
      name: project.name,
      description: project.description,
      bulletPoints: project.bulletPoints.join('\n'),
      tags: project.tags.join(', '),
      status: project.status,
      technologies: project.technologies.join(', '),
      link: project.link || ''
    })
    setShowModal(true)
  }

  const handleSaveProject = () => {
    if (!formData.name || !formData.description) {
      toast.error('Please fill in required fields')
      return
    }

    const techArray = formData.technologies.split(',').map(t => t.trim()).filter(t => t)
    const tagsArray = formData.tags.split(',').map(t => t.trim()).filter(t => t)
    const bulletArray = formData.bulletPoints.split('\n').map(b => b.trim()).filter(b => b)
    
    if (editingProject) {
      setProjects(projects.map(p => p.id === editingProject.id ? {
        ...p,
        name: formData.name,
        description: formData.description,
        bulletPoints: bulletArray,
        tags: tagsArray,
        status: formData.status,
        technologies: techArray,
        link: formData.link
      } : p))
      toast.success('Project updated!')
    } else {
      setProjects([...projects, {
        id: Date.now(),
        name: formData.name,
        description: formData.description,
        bulletPoints: bulletArray,
        tags: tagsArray,
        status: formData.status,
        technologies: techArray,
        link: formData.link
      }])
      toast.success('Project added!')
    }
    setShowModal(false)
  }

  const handleDeleteProject = (id: number) => {
    if (confirm('Are you sure you want to delete this project?')) {
      setProjects(projects.filter(p => p.id !== id))
      toast.success('Project deleted')
    }
  }

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active': return '#fb923c'
      case 'completed': return '#22c55e'
      case 'archived': return '#78716c'
      default: return '#78716c'
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
                padding: '8px 16px',
                borderRadius: '8px',
                background: 'transparent',
                border: '1px solid #e7e5e4',
                color: '#1c1917',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              ← Back
            </button>
            <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#1c1917' }}>Projects Manager</h1>
          </div>
          <button
            onClick={handleAddProject}
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
            + New Project
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 32px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
          {projects.map((project) => (
            <div
              key={project.id}
              style={{
                background: '#ffffff',
                borderRadius: '16px',
                padding: '24px',
                border: '1px solid #e7e5e4',
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.12)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)'
              }}
            >
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1c1917' }}>
                    {project.name}
                  </h3>
                  <span style={{
                    padding: '4px 12px',
                    borderRadius: '12px',
                    background: getStatusColor(project.status) + '20',
                    color: getStatusColor(project.status),
                    fontSize: '12px',
                    fontWeight: '600',
                    textTransform: 'capitalize'
                  }}>
                    {project.status}
                  </span>
                </div>
                <p style={{ color: '#78716c', fontSize: '14px', lineHeight: '1.5' }}>
                  {project.description}
                </p>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <p style={{ fontSize: '12px', fontWeight: '600', color: '#78716c', marginBottom: '8px' }}>
                  TECHNOLOGIES
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {project.technologies.map((tech, idx) => (
                    <span
                      key={idx}
                      style={{
                        padding: '4px 10px',
                        background: '#fafaf9',
                        border: '1px solid #e7e5e4',
                        borderRadius: '6px',
                        fontSize: '13px',
                        color: '#1c1917'
                      }}
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              {project.tags.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <p style={{ fontSize: '12px', fontWeight: '600', color: '#78716c', marginBottom: '8px' }}>
                    TAGS
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
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
                  </div>
                </div>
              )}

              {project.link && (
                <a
                  href={project.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'block',
                    color: '#1e3a8a',
                    fontSize: '14px',
                    textDecoration: 'none',
                    marginBottom: '16px',
                    fontWeight: '500'
                  }}
                >
                  View Project →
                </a>
              )}

              <div style={{ display: 'flex', gap: '8px', paddingTop: '16px', borderTop: '1px solid #e7e5e4' }}>
                <button
                  onClick={() => handleEditProject(project)}
                  style={{
                    flex: 1,
                    padding: '8px',
                    borderRadius: '6px',
                    background: 'transparent',
                    border: '1px solid #e7e5e4',
                    color: '#1c1917',
                    fontSize: '14px',
                    cursor: 'pointer',
                    fontWeight: '500'
                  }}
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteProject(project.id)}
                  style={{
                    flex: 1,
                    padding: '8px',
                    borderRadius: '6px',
                    background: 'transparent',
                    border: '1px solid #dc2626',
                    color: '#dc2626',
                    fontSize: '14px',
                    cursor: 'pointer',
                    fontWeight: '500'
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '20px'
        }}>
          <div style={{
            background: '#ffffff',
            borderRadius: '16px',
            padding: '32px',
            maxWidth: '600px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#1c1917', marginBottom: '24px' }}>
              {editingProject ? 'Edit Project' : 'New Project'}
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                  Project Name *
                </label>
                <input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="My Awesome Project"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e7e5e4',
                    fontSize: '15px',
                    background: '#fafaf9',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                  Description *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of the project..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e7e5e4',
                    fontSize: '15px',
                    background: '#fafaf9',
                    outline: 'none',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                  Key Achievements (one per line)
                </label>
                <textarea
                  value={formData.bulletPoints}
                  onChange={(e) => setFormData({ ...formData, bulletPoints: e.target.value })}
                  placeholder="Built responsive UI with React&#10;Integrated payment gateway&#10;Deployed on AWS with CI/CD"
                  rows={5}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e7e5e4',
                    fontSize: '15px',
                    background: '#fafaf9',
                    outline: 'none',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                  Tags (comma-separated)
                </label>
                <input
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  placeholder="web-dev, machine-learning, data-science"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e7e5e4',
                    fontSize: '15px',
                    background: '#fafaf9',
                    outline: 'none'
                  }}
                />
                <p style={{ fontSize: '12px', color: '#78716c', marginTop: '6px' }}>
                  Tags help filter projects when generating resumes for specific roles
                </p>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as Project['status'] })}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e7e5e4',
                    fontSize: '15px',
                    background: '#fafaf9',
                    outline: 'none'
                  }}
                >
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                  Technologies (comma-separated)
                </label>
                <input
                  value={formData.technologies}
                  onChange={(e) => setFormData({ ...formData, technologies: e.target.value })}
                  placeholder="React, Node.js, MongoDB"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e7e5e4',
                    fontSize: '15px',
                    background: '#fafaf9',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#1c1917', marginBottom: '8px' }}>
                  Project Link
                </label>
                <input
                  value={formData.link}
                  onChange={(e) => setFormData({ ...formData, link: e.target.value })}
                  placeholder="https://github.com/..."
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e7e5e4',
                    fontSize: '15px',
                    background: '#fafaf9',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '32px' }}>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  flex: 1,
                  padding: '12px',
                  borderRadius: '8px',
                  background: 'transparent',
                  border: '1px solid #e7e5e4',
                  color: '#1c1917',
                  fontWeight: '500',
                  cursor: 'pointer',
                  fontSize: '15px'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveProject}
                style={{
                  flex: 1,
                  padding: '12px',
                  borderRadius: '8px',
                  background: '#facc15',
                  border: 'none',
                  color: '#1e3a8a',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '15px'
                }}
              >
                {editingProject ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
