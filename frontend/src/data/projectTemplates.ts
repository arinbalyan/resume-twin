/**
 * Sample project templates for resume/portfolio
 * These templates provide pre-filled project examples that users can customize
 */

export interface ProjectTemplate {
  id: string;
  category: string;
  title: string;
  description: string;
  bulletPoints: string[];
  technologies: string[];
  tags: string[];
  suggestedLinks: {
    github?: string;
    live?: string;
  };
}

// Project categories for filtering
export const PROJECT_CATEGORIES = [
  { id: 'web', name: 'Web Development', icon: '🌐' },
  { id: 'mobile', name: 'Mobile Apps', icon: '📱' },
  { id: 'backend', name: 'Backend/API', icon: '⚙️' },
  { id: 'data', name: 'Data Science/ML', icon: '📊' },
  { id: 'devops', name: 'DevOps/Cloud', icon: '☁️' },
  { id: 'fullstack', name: 'Full Stack', icon: '💻' },
  { id: 'ai', name: 'AI/LLM', icon: '🤖' },
  { id: 'blockchain', name: 'Blockchain/Web3', icon: '🔗' },
  { id: 'game', name: 'Game Development', icon: '🎮' },
  { id: 'other', name: 'Other', icon: '📦' },
] as const;

// Sample project templates
export const PROJECT_TEMPLATES: ProjectTemplate[] = [
  // Web Development Projects
  {
    id: 'ecommerce-platform',
    category: 'web',
    title: 'E-Commerce Platform',
    description: 'A modern, scalable e-commerce platform with product management, cart functionality, and secure checkout',
    bulletPoints: [
      'Developed responsive UI with React and Tailwind CSS, achieving 95+ Lighthouse score',
      'Implemented real-time inventory management reducing stock discrepancies by 40%',
      'Integrated Stripe payment gateway with support for multiple currencies',
      'Built admin dashboard with analytics showing sales trends and user behavior',
      'Deployed on AWS with auto-scaling supporting 10,000+ concurrent users',
    ],
    technologies: ['React', 'Node.js', 'PostgreSQL', 'Redis', 'Stripe', 'AWS', 'Docker'],
    tags: ['fullstack', 'ecommerce', 'payments', 'react'],
    suggestedLinks: {
      github: 'https://github.com/username/ecommerce-platform',
      live: 'https://myshop.demo.com',
    },
  },
  {
    id: 'portfolio-builder',
    category: 'web',
    title: 'Portfolio Website Builder',
    description: 'Drag-and-drop portfolio builder with customizable themes and SEO optimization',
    bulletPoints: [
      'Created intuitive drag-and-drop interface using React DnD reducing setup time by 70%',
      'Implemented 15+ customizable themes with dark mode support',
      'Built SEO optimization tools improving average Google ranking by 30 positions',
      'Added custom domain support with automatic SSL certificate generation',
    ],
    technologies: ['Next.js', 'TypeScript', 'Prisma', 'Tailwind CSS', 'Cloudflare'],
    tags: ['web', 'saas', 'nextjs', 'typescript'],
    suggestedLinks: {
      github: 'https://github.com/username/portfolio-builder',
      live: 'https://portfoliobuilder.demo.com',
    },
  },
  {
    id: 'social-media-dashboard',
    category: 'web',
    title: 'Social Media Analytics Dashboard',
    description: 'Unified dashboard for tracking social media metrics across multiple platforms',
    bulletPoints: [
      'Aggregated data from Twitter, LinkedIn, Instagram APIs into single dashboard',
      'Built real-time engagement tracking with WebSocket updates every 30 seconds',
      'Implemented predictive analytics for optimal posting times using ML',
      'Created exportable reports in PDF and CSV formats',
    ],
    technologies: ['Vue.js', 'Python', 'FastAPI', 'Chart.js', 'PostgreSQL', 'Redis'],
    tags: ['analytics', 'dashboard', 'api-integration', 'vue'],
    suggestedLinks: {
      github: 'https://github.com/username/social-dashboard',
    },
  },

  // Mobile App Projects
  {
    id: 'fitness-tracker',
    category: 'mobile',
    title: 'Fitness Tracking App',
    description: 'Cross-platform fitness app with workout planning, progress tracking, and social features',
    bulletPoints: [
      'Built with React Native, achieving 98% code sharing between iOS and Android',
      'Integrated with Apple Health and Google Fit for automatic activity syncing',
      'Implemented offline-first architecture with sync when connected',
      'Added social features including workout sharing and friend challenges',
      'Achieved 4.7 star rating with 50,000+ downloads on App Store',
    ],
    technologies: ['React Native', 'TypeScript', 'Firebase', 'Redux', 'HealthKit', 'Google Fit API'],
    tags: ['mobile', 'react-native', 'health', 'firebase'],
    suggestedLinks: {
      github: 'https://github.com/username/fitness-tracker',
    },
  },
  {
    id: 'food-delivery-app',
    category: 'mobile',
    title: 'Food Delivery App',
    description: 'Feature-rich food delivery app with real-time order tracking and driver matching',
    bulletPoints: [
      'Developed customer app, restaurant dashboard, and driver app using Flutter',
      'Implemented real-time GPS tracking with Google Maps integration',
      'Built intelligent driver matching algorithm reducing delivery times by 25%',
      'Added payment integration with support for cards, UPI, and wallets',
    ],
    technologies: ['Flutter', 'Dart', 'Firebase', 'Google Maps API', 'Node.js', 'MongoDB'],
    tags: ['mobile', 'flutter', 'realtime', 'maps'],
    suggestedLinks: {
      github: 'https://github.com/username/food-delivery',
    },
  },

  // Backend/API Projects
  {
    id: 'api-gateway',
    category: 'backend',
    title: 'Microservices API Gateway',
    description: 'High-performance API gateway with authentication, rate limiting, and service discovery',
    bulletPoints: [
      'Designed gateway handling 100,000+ requests per second with sub-10ms latency',
      'Implemented JWT authentication with role-based access control',
      'Built intelligent rate limiting with Redis-backed sliding window algorithm',
      'Added automatic service discovery using Consul with health checks',
      'Created comprehensive logging and tracing with OpenTelemetry',
    ],
    technologies: ['Go', 'Redis', 'Consul', 'gRPC', 'OpenTelemetry', 'Docker', 'Kubernetes'],
    tags: ['backend', 'microservices', 'go', 'infrastructure'],
    suggestedLinks: {
      github: 'https://github.com/username/api-gateway',
    },
  },
  {
    id: 'rest-api-framework',
    category: 'backend',
    title: 'REST API Framework',
    description: 'Production-ready REST API framework with built-in authentication, validation, and documentation',
    bulletPoints: [
      'Created modular FastAPI-based framework reducing API development time by 60%',
      'Implemented automatic OpenAPI documentation with interactive testing',
      'Built comprehensive input validation with custom error messages',
      'Added async database support with connection pooling',
    ],
    technologies: ['Python', 'FastAPI', 'SQLAlchemy', 'Pydantic', 'PostgreSQL', 'Alembic'],
    tags: ['backend', 'python', 'fastapi', 'rest-api'],
    suggestedLinks: {
      github: 'https://github.com/username/api-framework',
    },
  },

  // Data Science/ML Projects
  {
    id: 'recommendation-engine',
    category: 'data',
    title: 'Product Recommendation Engine',
    description: 'ML-powered recommendation system using collaborative filtering and content-based approaches',
    bulletPoints: [
      'Developed hybrid recommendation algorithm combining user behavior and item features',
      'Processed 10M+ user interactions using Apache Spark for model training',
      'Achieved 35% improvement in click-through rate compared to baseline',
      'Implemented real-time inference API serving 1000+ recommendations/second',
      'Built A/B testing framework to validate model improvements',
    ],
    technologies: ['Python', 'TensorFlow', 'Apache Spark', 'Redis', 'FastAPI', 'MLflow'],
    tags: ['ml', 'data-science', 'recommendation', 'spark'],
    suggestedLinks: {
      github: 'https://github.com/username/recommendation-engine',
    },
  },
  {
    id: 'nlp-sentiment-analysis',
    category: 'data',
    title: 'Sentiment Analysis Platform',
    description: 'NLP platform for analyzing customer feedback and social media sentiment at scale',
    bulletPoints: [
      'Fine-tuned BERT model achieving 94% accuracy on domain-specific sentiment classification',
      'Processed 100,000+ documents daily using distributed inference with Ray',
      'Built interactive dashboard showing sentiment trends over time',
      'Implemented aspect-based sentiment analysis for granular insights',
    ],
    technologies: ['Python', 'PyTorch', 'Transformers', 'Hugging Face', 'Ray', 'FastAPI'],
    tags: ['nlp', 'ml', 'sentiment', 'transformers'],
    suggestedLinks: {
      github: 'https://github.com/username/sentiment-analyzer',
    },
  },
  {
    id: 'data-pipeline',
    category: 'data',
    title: 'Real-time Data Pipeline',
    description: 'Scalable ETL pipeline processing streaming data for analytics dashboards',
    bulletPoints: [
      'Designed event-driven architecture processing 1M+ events per minute',
      'Implemented data quality checks catching 99.5% of data anomalies',
      'Built exactly-once processing semantics ensuring data consistency',
      'Created monitoring dashboard with real-time pipeline health metrics',
    ],
    technologies: ['Apache Kafka', 'Apache Flink', 'Python', 'PostgreSQL', 'Grafana', 'Airflow'],
    tags: ['data-engineering', 'etl', 'kafka', 'streaming'],
    suggestedLinks: {
      github: 'https://github.com/username/data-pipeline',
    },
  },

  // DevOps/Cloud Projects
  {
    id: 'kubernetes-platform',
    category: 'devops',
    title: 'Kubernetes Platform',
    description: 'Production-ready Kubernetes platform with GitOps, monitoring, and auto-scaling',
    bulletPoints: [
      'Deployed and managed multi-cluster Kubernetes environment across 3 regions',
      'Implemented GitOps workflow with ArgoCD reducing deployment errors by 80%',
      'Built custom Prometheus/Grafana monitoring stack with 200+ alerts',
      'Created Terraform modules for reproducible infrastructure provisioning',
      'Achieved 99.99% uptime for critical workloads',
    ],
    technologies: ['Kubernetes', 'Terraform', 'ArgoCD', 'Prometheus', 'Grafana', 'Helm', 'AWS'],
    tags: ['devops', 'kubernetes', 'cloud', 'gitops'],
    suggestedLinks: {
      github: 'https://github.com/username/k8s-platform',
    },
  },
  {
    id: 'ci-cd-platform',
    category: 'devops',
    title: 'CI/CD Pipeline Platform',
    description: 'Automated CI/CD platform supporting multiple languages and deployment targets',
    bulletPoints: [
      'Built reusable pipeline templates reducing setup time from days to hours',
      'Implemented automatic security scanning catching vulnerabilities before deployment',
      'Created rollback automation reducing incident recovery time by 70%',
      'Added cost optimization features saving $50K/month in cloud costs',
    ],
    technologies: ['GitHub Actions', 'Jenkins', 'Docker', 'Kubernetes', 'Trivy', 'SonarQube'],
    tags: ['devops', 'ci-cd', 'automation', 'security'],
    suggestedLinks: {
      github: 'https://github.com/username/cicd-platform',
    },
  },

  // AI/LLM Projects
  {
    id: 'chatbot-framework',
    category: 'ai',
    title: 'AI Chatbot Framework',
    description: 'Customizable AI chatbot framework with RAG and multi-model support',
    bulletPoints: [
      'Built modular chatbot framework supporting GPT-4, Claude, and Llama models',
      'Implemented RAG pipeline with vector search achieving 92% answer accuracy',
      'Created conversation memory system for context-aware responses',
      'Added multi-language support with automatic translation',
      'Deployed on AWS with auto-scaling handling 10,000+ concurrent conversations',
    ],
    technologies: ['Python', 'LangChain', 'OpenAI', 'Pinecone', 'FastAPI', 'Redis', 'AWS'],
    tags: ['ai', 'llm', 'chatbot', 'rag'],
    suggestedLinks: {
      github: 'https://github.com/username/ai-chatbot',
      live: 'https://chatbot.demo.com',
    },
  },
  {
    id: 'code-assistant',
    category: 'ai',
    title: 'AI Code Assistant',
    description: 'VS Code extension providing AI-powered code completion and refactoring suggestions',
    bulletPoints: [
      'Developed VS Code extension with inline code suggestions and chat interface',
      'Fine-tuned CodeLlama model on company codebase improving relevance by 40%',
      'Implemented context-aware suggestions using AST analysis',
      'Added code review automation catching common issues before PR',
    ],
    technologies: ['TypeScript', 'Python', 'VS Code API', 'CodeLlama', 'Tree-sitter', 'FastAPI'],
    tags: ['ai', 'developer-tools', 'vscode', 'code-completion'],
    suggestedLinks: {
      github: 'https://github.com/username/code-assistant',
    },
  },

  // Full Stack Projects
  {
    id: 'project-management',
    category: 'fullstack',
    title: 'Project Management Tool',
    description: 'Collaborative project management platform with real-time updates and automation',
    bulletPoints: [
      'Built Kanban and Gantt views with drag-and-drop functionality',
      'Implemented real-time collaboration using WebSockets for instant updates',
      'Created automation engine for repetitive tasks and notifications',
      'Added time tracking and reporting features with export capabilities',
      'Integrated with Slack, GitHub, and Jira for seamless workflow',
    ],
    technologies: ['Next.js', 'Node.js', 'PostgreSQL', 'WebSocket', 'Redis', 'AWS'],
    tags: ['fullstack', 'saas', 'collaboration', 'productivity'],
    suggestedLinks: {
      github: 'https://github.com/username/project-manager',
      live: 'https://projectmanager.demo.com',
    },
  },
  {
    id: 'video-streaming',
    category: 'fullstack',
    title: 'Video Streaming Platform',
    description: 'Netflix-like video streaming platform with adaptive bitrate and content management',
    bulletPoints: [
      'Developed video player with adaptive bitrate streaming using HLS',
      'Built content management system for uploading and transcoding videos',
      'Implemented recommendation engine based on viewing history',
      'Created monetization features including subscriptions and pay-per-view',
      'Achieved 99.9% video playback success rate across devices',
    ],
    technologies: ['React', 'Node.js', 'FFmpeg', 'AWS MediaConvert', 'CloudFront', 'MongoDB'],
    tags: ['fullstack', 'streaming', 'video', 'media'],
    suggestedLinks: {
      github: 'https://github.com/username/video-platform',
    },
  },

  // Blockchain/Web3 Projects
  {
    id: 'nft-marketplace',
    category: 'blockchain',
    title: 'NFT Marketplace',
    description: 'Decentralized NFT marketplace with minting, trading, and auction features',
    bulletPoints: [
      'Built smart contracts in Solidity with comprehensive testing (100% coverage)',
      'Implemented gasless minting using meta-transactions',
      'Created Dutch and English auction mechanisms for NFT sales',
      'Integrated with IPFS for decentralized metadata storage',
      'Processed $1M+ in transactions with zero security incidents',
    ],
    technologies: ['Solidity', 'React', 'ethers.js', 'Hardhat', 'IPFS', 'The Graph'],
    tags: ['blockchain', 'web3', 'nft', 'solidity'],
    suggestedLinks: {
      github: 'https://github.com/username/nft-marketplace',
    },
  },
  {
    id: 'defi-protocol',
    category: 'blockchain',
    title: 'DeFi Lending Protocol',
    description: 'Decentralized lending protocol with yield optimization and governance',
    bulletPoints: [
      'Designed and deployed lending pool smart contracts on Ethereum',
      'Implemented dynamic interest rate model based on utilization',
      'Created governance token with voting and proposal mechanisms',
      'Built analytics dashboard showing TVL, APY, and user positions',
      'Achieved $10M+ Total Value Locked within first month',
    ],
    technologies: ['Solidity', 'TypeScript', 'React', 'Chainlink', 'OpenZeppelin', 'Foundry'],
    tags: ['blockchain', 'defi', 'lending', 'smart-contracts'],
    suggestedLinks: {
      github: 'https://github.com/username/defi-lending',
    },
  },

  // Game Development Projects
  {
    id: 'multiplayer-game',
    category: 'game',
    title: 'Multiplayer Strategy Game',
    description: 'Real-time multiplayer strategy game with matchmaking and ranking system',
    bulletPoints: [
      'Developed game engine in Unity with custom networking layer',
      'Implemented authoritative server preventing cheating and exploits',
      'Built ELO-based matchmaking system for fair competitive play',
      'Created procedural map generation for endless replayability',
      'Achieved 50,000+ downloads with 4.5 star rating',
    ],
    technologies: ['Unity', 'C#', 'Photon', 'Node.js', 'MongoDB', 'AWS GameLift'],
    tags: ['game', 'unity', 'multiplayer', 'strategy'],
    suggestedLinks: {
      github: 'https://github.com/username/strategy-game',
    },
  },

  // Open Source/Library Projects
  {
    id: 'ui-component-library',
    category: 'other',
    title: 'React UI Component Library',
    description: 'Accessible, customizable React component library with comprehensive documentation',
    bulletPoints: [
      'Created 50+ accessible components following WAI-ARIA standards',
      'Built theme system with support for custom color palettes and dark mode',
      'Achieved 100% test coverage with visual regression testing',
      'Published to npm with 5,000+ weekly downloads',
      'Documented all components with Storybook interactive examples',
    ],
    technologies: ['React', 'TypeScript', 'Storybook', 'Rollup', 'Jest', 'CSS-in-JS'],
    tags: ['open-source', 'react', 'component-library', 'accessibility'],
    suggestedLinks: {
      github: 'https://github.com/username/ui-library',
      live: 'https://ui-library.demo.com',
    },
  },
  {
    id: 'cli-tool',
    category: 'other',
    title: 'Developer CLI Tool',
    description: 'Command-line tool for automating common development workflows',
    bulletPoints: [
      'Built cross-platform CLI with intuitive commands and helpful error messages',
      'Implemented plugin system allowing community extensions',
      'Added project scaffolding with 10+ starter templates',
      'Created auto-update mechanism for seamless version management',
      'Documented with man pages and --help for all commands',
    ],
    technologies: ['Rust', 'Clap', 'Tokio', 'serde', 'GitHub API'],
    tags: ['cli', 'developer-tools', 'rust', 'automation'],
    suggestedLinks: {
      github: 'https://github.com/username/dev-cli',
    },
  },
];

/**
 * Get project templates by category
 */
export const getProjectsByCategory = (category: string): ProjectTemplate[] => {
  return PROJECT_TEMPLATES.filter(p => p.category === category);
};

/**
 * Search project templates by query
 */
export const searchProjectTemplates = (query: string): ProjectTemplate[] => {
  const lowerQuery = query.toLowerCase();
  return PROJECT_TEMPLATES.filter(p => 
    p.title.toLowerCase().includes(lowerQuery) ||
    p.description.toLowerCase().includes(lowerQuery) ||
    p.technologies.some(t => t.toLowerCase().includes(lowerQuery)) ||
    p.tags.some(t => t.toLowerCase().includes(lowerQuery))
  );
};

/**
 * Get a random project template
 */
export const getRandomTemplate = (): ProjectTemplate => {
  return PROJECT_TEMPLATES[Math.floor(Math.random() * PROJECT_TEMPLATES.length)];
};

export default PROJECT_TEMPLATES;
