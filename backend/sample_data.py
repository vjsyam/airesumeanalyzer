# Production Presets for Resumes and Job Descriptions (All Generic Candidate Profiles)

SAMPLE_RESUMES = {
    "fullstack_ai_dev": {
        "title": "Full-Stack & AI Developer (React, FastAPI, LLM Inference)",
        "filename": "FullStack_AI_Developer_Resume.pdf",
        "candidate_name": "Jordan Lee",
        "text": """JORDAN LEE
jordan.lee.dev@gmail.com | +1 (555) 432-8765 | San Francisco, CA
linkedin.com/in/jordanlee-dev | github.com/jordanlee-ai

PROFESSIONAL SUMMARY
Full-Stack Software Engineer with focus on building responsive web applications, high-performance Python/Node.js backend APIs, and LLM-powered developer tools.

TECHNICAL SKILLS
Languages: Python, TypeScript, JavaScript, SQL, C++, HTML/CSS
Frontend: React, Next.js, Tailwind CSS, Vite, Redux Toolkit
Backend: FastAPI, Node.js, Express, Flask, RESTful APIs, WebSockets
Databases: PostgreSQL, MongoDB, Redis, Supabase
AI & Infrastructure: Gemini API, LangChain, OpenAI API, Docker, Git, Vercel, AWS

TECHNICAL PROJECTS

AI Resume Telemetry & ATS Scoring Engine
- Built a full-stack web application with React and FastAPI to parse PDF/DOCX resumes and evaluate ATS scores.
- Integrated Google Gemini API for skill extraction, job description gap analysis, and bullet rewrites.
- Applied rule-based humanization algorithms to scrub corporate clichés and format output for ATS readability.
- Implemented temporary file lifecycle management and server-side document parsing using pdfplumber and python-docx.

High-Throughput URL Analytics Platform
- Developed a URL shortener with custom aliases and QR code generation using FastAPI and PostgreSQL.
- Implemented sliding-window rate limiting and request throttling with Redis to prevent API abuse.
- Designed responsive telemetry dashboard in React to display real-time click analytics and geographic referrers.
- Optimized database indexing on lookup keys, keeping p95 query latencies under 15ms.

Automated Code Review Agent
- Created an automated code review bot using Python and LLM tool calling to detect syntax flaws and security vulnerabilities.
- Integrated GitHub Webhooks to post inline review comments on pull requests.
- Wrote unit test suites achieving 92% coverage across parsing and token-tracking modules.

EDUCATION
B.S. in Computer Science | University of California | GPA: 3.8 / 4.0
"""
    },
    "backend_engineer": {
        "title": "Senior Backend Engineer (Distributed Systems, 5+ Yrs)",
        "filename": "Senior_Backend_Engineer_Resume.pdf",
        "candidate_name": "Alex Vance",
        "text": """ALEX VANCE
alex.vance@devmail.io | +1 (555) 321-9876 | Seattle, WA
linkedin.com/in/alexvance-dev | github.com/alexvance-core

PROFESSIONAL SUMMARY
Backend Software Engineer with 5+ years of experience designing scalable RESTful APIs, distributed microservices, and database layers for high-throughput cloud environments.

TECHNICAL SKILLS
Languages: Python, Go, SQL, JavaScript
Frameworks & Libraries: FastAPI, Django, Flask, Express.js, PyTest
Databases: PostgreSQL, MySQL, Redis, DynamoDB
DevOps & Cloud: Docker, Kubernetes, AWS (EC2, S3, RDS), Git, GitHub Actions, Terraform
Methodologies: RESTful Architecture, Microservices, CI/CD, Agile/Scrum

PROFESSIONAL EXPERIENCE

Senior Backend Engineer | CloudScale Systems | Jan 2022 - Present
- Designed and maintained high-throughput REST APIs in FastAPI, serving over 18 million requests daily with 99.98% uptime.
- Worked on backend caching layers and fixed latency bottlenecks in high-volume microservices.
- Led migration of legacy monolithic endpoints to decoupled microservices running inside containerized Docker pods.
- Optimized slow SQL queries in PostgreSQL, reducing query latency by 35% on critical analytics dashboard views.
- Mentored junior engineers and conducted peer code reviews across backend teams.

Backend Engineer | FinTech Pulse | Jun 2019 - Dec 2021
- Developed payment settlement pipelines using Python, PostgreSQL, and RabbitMQ message queues.
- Integrated third-party payment gateways including Stripe and Plaid with idempotency protections.
- Maintained database tables and improved system performance during month-end audit processing.
- Configured automated GitHub Actions workflows to execute linting and unit test suites on every pull request.

KEY PROJECTS

Distributed Task Orchestrator (Open Source)
- Built an open-source task worker queue in Python with Redis backend, achieving sub-5ms job scheduling.
- Gained 400+ stars on GitHub and contributions from 12 community developers.

EDUCATION
B.S. in Computer Science | University of Washington | 2015 - 2019
"""
    },
    "frontend_specialist": {
        "title": "Senior Frontend Engineer (React, Design Systems, Web Vitals)",
        "filename": "Frontend_Specialist_Resume.docx",
        "candidate_name": "Morgan Reed",
        "text": """MORGAN REED
morgan.reed@codecraft.org | +1 (415) 890-1234 | Austin, TX
linkedin.com/in/morganreed-eng | github.com/morganreed

PROFESSIONAL SUMMARY
Frontend Engineer specializing in accessible design systems, client performance optimization, and responsive developer tooling interfaces in React and TypeScript.

CORE COMPETENCIES
Frontend: React, Next.js, TypeScript, JavaScript, Tailwind CSS, HTML5, CSS3, Redux Toolkit
Backend: Node.js, Express, Python, REST APIs, GraphQL
Storage & Tools: PostgreSQL, Redis, Docker, Git, Jest, Vitest, Vercel

WORK EXPERIENCE

Senior Frontend Developer | Nexa Digital | 2021 - Present
- Built customer-facing dashboard features and developer workspaces using React, TypeScript, and modern CSS.
- Architected accessible UI design token library, reducing frontend code redundancy across 8 distinct web applications.
- Collaborated with product designers in Figma to build keyboard-accessible, dark-mode-first components.
- Reduced initial bundle size by 42% through aggressive code splitting, tree shaking, and dynamic imports.

Software Developer | ByteWorks Solutions | 2019 - 2021
- Created internal tooling and analytics portals using React, TypeScript, and Node.js.
- Wrote automated unit and integration tests using Jest and React Testing Library, maintaining 88% test coverage.
- Supported continuous delivery pipelines and optimized Core Web Vitals to achieve 98+ Google Lighthouse scores.

EDUCATION
B.S. in Software Engineering | University of Texas at Austin
"""
    },
    "ai_ml_engineer": {
        "title": "Machine Learning Engineer (LLMs, RAG, PyTorch)",
        "filename": "ML_Engineer_Resume.pdf",
        "candidate_name": "Elena Rostova",
        "text": """ELENA ROSTOVA
elena.rostova@ailabs.org | +1 (650) 432-8765 | San Francisco, CA
linkedin.com/in/elenarostova-ml | github.com/elena-ai

PROFESSIONAL SUMMARY
Machine Learning Engineer specializing in Large Language Model (LLM) fine-tuning, retrieval-augmented generation (RAG), and vector search infrastructure.

TECHNICAL SKILLS
Languages: Python, C++, SQL, Bash
ML & AI: PyTorch, Hugging Face Transformers, LangChain, LlamaIndex, vLLM, DeepSpeed
Vector Databases: Pinecone, Qdrant, Milvus, ChromaDB, pgvector
Infrastructure: Docker, Kubernetes, AWS SageMaker, Ray, Triton Inference Server

EXPERIENCE

Machine Learning Engineer | Cognition AI | 2022 - Present
- Architected enterprise RAG system processing 250k daily documents using hybrid dense-sparse vector retrieval.
- Fine-tuned open-source LLMs using LoRA and QLoRA on domain datasets, improving factual accuracy by 28%.
- Optimized inference latencies using vLLM and dynamic batching on NVIDIA A100 GPUs, cutting p99 latency from 450ms to 110ms.
- Built automated evaluation harness measuring hallucinations, retrieval precision, and ground truth alignment.

AI Research Intern | Stanford AI Lab | 2021 - 2022
- Conducted experiments on contrastive learning and multi-modal embedding models.
- Co-authored paper on sample-efficient fine-tuning published at NeurIPS workshop.

EDUCATION
M.S. in Artificial Intelligence | Stanford University
B.S. in Computer Science | UC Berkeley
"""
    }
}

SAMPLE_JOB_DESCRIPTIONS = {
    "software_developer": {
        "title": "Software Developer (Core Engineering & Applications)",
        "company": "CoreTech Solutions",
        "level": "Mid-Level",
        "tags": ["Python", "JavaScript", "SQL", "REST APIs", "Git", "Docker"],
        "text": """CoreTech Solutions is looking for a versatile Software Developer to join our core product engineering team. You will develop, maintain, and scale robust software applications across both web services and database systems.

Key Responsibilities:
- Design, develop, and deploy scalable software features and RESTful APIs using Python, JavaScript/TypeScript, or Java.
- Write clean, maintainable, and well-tested code backed by automated unit and integration tests.
- Design relational database schemas and optimize SQL queries (PostgreSQL / MySQL) for high throughput.
- Collaborate across cross-functional teams in an agile environment, participating in daily standups and peer code reviews.
- Troubleshoot production issues, analyze error logs, and optimize application performance and latency.
- Containerize application components using Docker and support automated CI/CD deployment pipelines.

Requirements:
- 2+ years of professional software development experience.
- Strong proficiency in at least one modern language: Python, JavaScript/TypeScript, Java, or C++.
- Practical knowledge of relational databases (SQL, indexing, query optimization).
- Hands-on experience with RESTful API architecture, Git version control, and automated testing frameworks.
- Familiarity with containerization (Docker) and cloud deployments (AWS, GCP, or Azure) is a plus.
- Solid analytical thinking, problem-solving skills, and proactive communication.
"""
    },
    "fullstack_ai": {
        "title": "Full-Stack AI Application Engineer",
        "company": "Kinetik Labs",
        "level": "Mid-Senior",
        "tags": ["React", "FastAPI", "Gemini API", "Vector DB", "TypeScript"],
        "text": """Kinetik Labs is hiring a Full-Stack Engineer to build user-facing generative AI tools and developer platforms.

Key Responsibilities:
- Develop modern, responsive web interfaces in React and TypeScript.
- Build resilient backend APIs in Python (FastAPI) or Node.js orchestrating LLM inference workflows.
- Integrate vector search databases and caching systems for retrieval-augmented generation.
- Implement robust authentication, rate limiting, and real-time streaming interfaces (WebSockets / Server-Sent Events).
- Optimize client-side rendering performance and interaction responsiveness.

Minimum Qualifications:
- 2+ years experience building web applications with React, TypeScript, and Python or Node.js.
- Experience consuming or integrating LLM APIs (Gemini, Claude, or OpenAI).
- Proficiency with SQL databases (PostgreSQL) and containerization with Docker.
- Passion for crafting clean, human-centered developer interfaces.
"""
    },
    "staff_backend": {
        "title": "Senior Backend Engineer (Distributed Systems)",
        "company": "Voxel Dynamics",
        "level": "Senior",
        "tags": ["FastAPI", "Go", "Kafka", "PostgreSQL", "Kubernetes"],
        "text": """Voxel Dynamics is looking for a Senior Backend Engineer to join our Core Platform team. You will architect and build mission-critical distributed systems that process terabytes of real-time telemetry.

Responsibilities:
- Build resilient, horizontally scalable REST and gRPC microservices in Python (FastAPI) or Go.
- Architect high-performance distributed caching using Redis and event streaming pipelines with Apache Kafka.
- Design relational schemas and optimize complex queries in PostgreSQL at scale.
- Deploy and manage containerized applications using Kubernetes and Docker on AWS cloud infrastructure.
- Lead system design reviews, establish latency SLAs (p99 < 50ms), and champion engineering excellence.

Requirements:
- 4+ years of professional backend engineering experience.
- Strong proficiency in Python (FastAPI/Django) or Go.
- Practical experience with PostgreSQL query tuning, indexing, and connection pooling.
- Hands-on expertise with distributed message brokers (Kafka or RabbitMQ) and caching strategies (Redis).
- Proven familiarity with Docker, Kubernetes, and AWS infrastructure (EC2, EKS, RDS).
- Solid grasp of distributed tracing, observability (Prometheus/Grafana), and CI/CD automation.
"""
    },
    "frontend_react": {
        "title": "Senior Frontend Engineer (Web Architecture & UI)",
        "company": "Vercel / Linear Partner",
        "level": "Senior",
        "tags": ["React", "Next.js", "TypeScript", "Performance", "CSS Architecture"],
        "text": """We are seeking a Frontend Engineer obsessed with craft, typography, responsiveness, and performance. You will build clean, fast developer tooling surfaces used by thousands of engineering teams daily.

Responsibilities:
- Architect modular component libraries in React and TypeScript with zero unnecessary dependencies.
- Build highly responsive, accessible, dark-mode-first user interfaces with smooth micro-interactions.
- Optimize web vitals: achieve sub-100ms interaction latencies, 60fps animations, and minimal bundle footprints.
- Collaborate closely with product designers to translate Figma tokens into clean CSS variables and primitives.
- Write thorough unit and integration test suites using Vitest and React Testing Library.

Qualifications:
- 3+ years of professional frontend experience with React and TypeScript.
- Deep mastery of modern CSS (CSS Grid, Flexbox, custom properties, animations) without reliance on heavy UI component bloat.
- Proven experience with state management, client caching, and optimistic UI updates.
- Eye for typography, spacing hierarchy, and keyboard-driven developer experiences.
"""
    },
    "ml_llm_engineer": {
        "title": "Machine Learning Engineer (LLMs & RAG)",
        "company": "ScaleAI Foundation Team",
        "level": "Mid-Senior",
        "tags": ["PyTorch", "Hugging Face", "vLLM", "Pinecone", "LangChain"],
        "text": """Join our generative AI foundation team building production RAG pipelines and fine-tuned open-source model deployments.

Responsibilities:
- Build and evaluate scalable Retrieval-Augmented Generation (RAG) architectures with hybrid dense/sparse search.
- Fine-tune foundation models (Llama, Mistral) using LoRA, QLoRA, and supervised instruction tuning.
- Deploy high-throughput inference endpoints using vLLM, TensorRT-LLM, and Triton on GPU clusters.
- Design hallucination benchmarks, prompt evaluations, and automated guardrail systems.
- Collaborate with backend engineers to integrate low-latency model inference into customer-facing APIs.

Requirements:
- 3+ years experience with Python, PyTorch, and the Hugging Face ecosystem.
- Deep understanding of transformer architectures, attention mechanisms, and tokenization.
- Experience with vector databases (Pinecone, Qdrant, Milvus, or pgvector).
- Hands-on experience optimizing GPU memory and batching inference.
"""
    },
    "devops_platform": {
        "title": "Cloud Platform & DevOps Engineer",
        "company": "Datadog Cloud Platform",
        "level": "Senior",
        "tags": ["Kubernetes", "Terraform", "AWS", "Docker", "CI/CD"],
        "text": """We are looking for a Platform & DevOps Engineer to scale our multi-region Kubernetes infrastructure and CI/CD developer platforms.

Responsibilities:
- Maintain and scale multi-cluster Kubernetes environments on AWS (EKS).
- Automate cloud infrastructure using Terraform and GitOps (ArgoCD).
- Build zero-downtime CI/CD pipelines in GitHub Actions for automated testing, container scanning, and canary deployments.
- Implement comprehensive observability using Prometheus, Grafana, OpenTelemetry, and Jaeger distributed tracing.
- Enforce infrastructure security policies, IAM least-privilege access, and automated secrets management.

Requirements:
- 3+ years experience administering Linux, Docker, and production Kubernetes clusters.
- Strong proficiency with Terraform (Infrastructure as Code) and AWS cloud services.
- Experience writing automation scripts in Python, Bash, or Go.
- Solid understanding of network security, TLS, VPC peering, and ingress controllers.
"""
    },
    "junior_software_eng": {
        "title": "Associate / Junior Software Engineer",
        "company": "Cloudflare / Shopify",
        "level": "Entry / Early Career",
        "tags": ["Python", "JavaScript", "SQL", "Git", "REST APIs"],
        "text": """We are seeking an enthusiastic Associate Software Engineer to join our core product engineering team. This role is ideal for ambitious early-career developers or recent graduates with strong computer science foundations.

Responsibilities:
- Develop features across frontend and backend services in Python, JavaScript/TypeScript, or Go.
- Write clean, maintainable, and well-tested code with unit and integration test coverage.
- Collaborate with senior engineers through regular pull request code reviews and design sessions.
- Assist in investigating bugs, monitoring error dashboards, and optimizing database queries.
- Participate in agile sprints, daily standups, and retrospective meetings.

Requirements:
- Degree in Computer Science, Software Engineering, or equivalent practical project experience.
- Solid understanding of data structures, algorithms, and object-oriented programming.
- Familiarity with RESTful APIs, Git version control, and relational databases (PostgreSQL or MySQL).
- Strong problem-solving mindset, curiosity, and willingness to learn modern developer workflows.
"""
    }
}
