# Fernando Rubén Canal Mendoza — CV

> **Título:** AI Software Engineer / Applied ML Engineer
> **Enfoque:** Construir productos inteligentes que escalan en producción
> **Tagline:** "Building AI that ships to production"
> **Idiomas:** Español (nativo), Inglés (B2)

---

## Resumen Profesional

Ingeniero de software con base sólida en backend (Java/Spring Boot, Python/FastAPI) evolucionando hacia AI Engineering. Especializado en el diseño de sistemas escalables basados en arquitecturas de microservicios y monolitos modulares, desarrollo de APIs RESTful seguras y mantenibles, y construcción de componentes desacoplados para entornos distribuidos. Experiencia en sistemas RAG, orquestación de LLMs con LangChain, y despliegue de aplicaciones inteligentes con Docker/Kubernetes. Complemento este perfil con conocimientos en procesamiento de datos y machine learning aplicado, aportando soluciones backend robustas, inteligentes y orientadas a alta disponibilidad.

---

## Experiencia Laboral

### Backend & Software Engineer — PHAXSI
**Período:** Dic 2025 – Presente
**Responsabilidades:**
- Arquitectura y refactorización de un backend monolítico (~3,200 LOC) hacia una arquitectura modular orientada a dominios, con definición de capas y manejo centralizado de errores, mejorando la mantenibilidad y escalabilidad del sistema.
- Optimización y desarrollo de un pipeline de reportes geoespaciales, logrando una mejora de rendimiento de 10× mediante la vectorización de operaciones a nivel de píxel con NumPy/SciPy y la reducción de llamadas a LLM, eliminando errores por cuota.
- Diseño e implementación de un microservicio de pasarela de pagos (patrón Adapter) con soporte multimoneda (USD/PEN), integración de tipo de cambio en tiempo real (API SUNAT) y controles transaccionales robustos (idempotencia, bloqueos a nivel de fila), mitigando riesgos de doble gasto en entornos de alta concurrencia.
- Fortalecimiento de la confiabilidad y seguridad del sistema mediante el desarrollo de 275 pruebas unitarias automatizadas, ejecución de pruebas de estrés (7 escenarios) para identificación de cuellos de botella, e implementación de hardening de infraestructura (rate limiting, connection pooling, estrategias de reintento), mejorando la estabilidad bajo carga.
**Tecnologías:** Python, FastAPI, SQLModel, Alembic, MySQL, Redis, Pytest, Locust, Docker, Linux, Vertex API, Mercado Pago.

### Data Scientist — Anyone AI (Part Time)
**Período:** Jul 2025 – Nov 2025
**Responsabilidades:**
- Desarrollo de proyectos de machine learning aplicando regresión, clasificación y redes neuronales con Python, Scikit-learn, TensorFlow y PyTorch, logrando mejoras de hasta 15% en accuracy sobre datos reales.
- Implementación de pipelines de preprocesamiento y ETL (limpieza, feature engineering, normalización) que mejoraron la calidad de los datos y el desempeño de los modelos.
- Diseño y evaluación de modelos usando métricas clave (accuracy, F1-score), realizando optimización de hiperparámetros y comparando arquitecturas para resultados listos para producción.
- Liderazgo técnico en el desarrollo de un sistema RAG (Retrieval-Augmented Generation) para consultas de pólizas de seguros. Diseñé la arquitectura de recuperación vectorial con OpenSearch y la orquestación de LLMs mediante LangChain, entregando una solución de IA Generativa escalable.
**Tecnologías:** Python, Pandas, LangChain, Haystack, OpenSearch, FastAPI, NumPy, Scikit-Learn, TensorFlow, PyTorch, Docker, EC2, RDS, Elastic Beanstalk.

### Backend Developer — SmartPressure (Freelance)
**Período:** Dic 2024 – Mar 2025
**Responsabilidades:**
- Diseño e implementación de una API REST en Spring Boot/Java para una plataforma de telemedicina ("SmartPressure"), implementando una arquitectura estricta en capas para asegurar mantenibilidad y desacoplamiento.
- Gestión de la evolución del esquema de base de datos PostgreSQL mediante migraciones versionadas con Flyway, garantizando integridad de datos entre entornos de desarrollo y producción.
- Implementación de procesamiento asíncrono para el sistema de notificaciones y alertas médicas, optimizando los tiempos de respuesta de la API principal y evitando bloqueos.
- Desarrollo y ejecución de pruebas unitarias con JUnit/Mockito, elevando la cobertura por encima del 85% y disminuyendo bugs en producción.
**Tecnologías:** Java, Spring Boot 3, PostgreSQL, Flyway, Docker, GitHub, JUnit.

### Desarrollador Backend — Freelance
**Período:** Set 2024 – Dic 2024
**Responsabilidades:**
- Desarrollo de un backend escalable en Spring Boot para catálogo de productos, carrito de compras y gestión de pedidos, permitiendo operaciones e-commerce fluidas y mejores tiempos de respuesta.
- Construcción de un panel de administración en React con CRUD completo y dashboards en tiempo real, mejorando la gestión de productos y ofreciendo métricas útiles a los stakeholders.
- Orquestación de servicios conteinerizados con Docker Compose para asegurar entornos consistentes de desarrollo y despliegue.
- Configuración de un pipeline básico de CI para automatizar build e integración, disminuyendo errores manuales y acelerando los ciclos de despliegue.
**Tecnologías:** Java, Spring Boot, PostgreSQL, Hibernate/JPA, Docker, JUnit, Mockito, GitHub.

---

## Educación

### Ingeniería de Sistemas — Universidad Nacional de San Agustín (UNSA)
**Año:** 2025

---

## Skills Técnicos

### AI / Machine Learning
- Sistemas RAG (Retrieval-Augmented Generation)
- LangChain, Haystack — orquestación de LLMs y agentes
- PyTorch, TensorFlow, Scikit-Learn — frameworks de ML/DL
- FAISS, ChromaDB — bases de datos vectoriales
- OpenSearch — búsqueda semántica e híbrida
- Fine-tuning con LoRA/QLoRA
- Sentence Transformers — embeddings
- Pandas, NumPy — procesamiento de datos

### Backend Engineering
- Python / FastAPI / Pydantic / SQLModel
- Java / Spring Boot 3 / Hibernate/JPA
- APIs RESTful seguras
- PostgreSQL, MySQL, Redis — bases de datos
- Alembic, Flyway — migraciones versionadas
- Patrones de diseño limpio, arquitectura por capas

### Infraestructura & MLOps
- Docker, Docker Compose
- Kubernetes (EKS/AKS)
- AWS (EC2, RDS, Elastic Beanstalk)
- GitHub Actions, Jenkins, Azure DevOps — CI/CD
- Terraform — Infrastructure as Code
- SonarQube — análisis estático
- Nginx — reverse proxy
- Linux

### Frontend
- Vue 3 (Composition API)
- React
- Tailwind CSS
- Chart.js — visualización de datos

### Herramientas & Testing
- Git, GitHub
- Pytest, Locust — testing Python
- JUnit, Mockito — testing Java
- Metodologías ágiles: Scrum, Kanban

---

## Certificaciones / Formación

### Aprendizaje por Refuerzo con Python — CODAERUS
**Contenido:** MDPs, Programación Dinámica, Monte Carlo, SARSA, Q-Learning, Deep Q-Network (DQN), REINFORCE, A2C.
**Conexión:** Base técnica para RLHF, usado para alinear LLMs modernos.

### Especialista en DevOps Multicloud — TecyLab
**Duración:** 25 horas cronológicas · 10 sesiones en vivo vía Zoom (lunes y jueves)
**Inicio:** 30 de abril de 2025
**Descripción:** Formación técnica para profesionales de TI orientada a dominar la implementación de arquitecturas para despliegues continuos en entornos multicloud (AWS y Azure).
**Contenido:**
- Fundamentos de DevSecOps y cultura DevOps
- Contenerización con Docker y orquestación con Kubernetes (EKS/AKS)
- Automatización CI/CD con Jenkins, GitHub Actions y Azure DevOps
- Infraestructura como Código (IaC) con Terraform
- Análisis de calidad de código con SonarQube
- Despliegue de aplicaciones en entornos AWS y Azure
**Beneficios:** Acceso ilimitado a grabaciones de las sesiones, certificado con validación QR y garantía de recursar sin costo.

### Desarrollo de Soluciones de IA de Nueva Generación con Agentes — AnyoneAI
**Año:** 2025
**Enfoque:** Desarrollo de soluciones de inteligencia artificial basadas en agentes autónomos.

### Desarrollo de Aplicaciones basadas en LLMs — AnyoneAI
**Año:** 2025
**Enfoque:** Construcción de aplicaciones sobre modelos de lenguaje de gran escala (LLM).

### Programación Senior con Spring Boot en Multicloud y Microservicios — TecyLab
**Año:** 2024
**Enfoque:** Desarrollo avanzado con Spring Boot, arquitecturas de microservicios y despliegues multicloud.

### Oracle Next Education F2 T4 Back-end — Alura Latam
**Año:** 2023
**Enfoque:** Formación intensiva en desarrollo backend con Java y Spring.

---

## Proyectos Destacados

### Auto Profiling + AI Layer
Plataforma que visualiza análisis de datos como dashboards interactivos con agente AI integrado. El agente explica dashboards en lenguaje natural, implementa RAG sobre Data Contracts para búsqueda semántica, y cuenta con un Model Service para predicciones con explicaciones LLM.
- **Stack:** FastAPI, Vue 3, Chart.js, LangChain, FAISS, Docker
- **Demuestra:** RAG, Agents, Model Serving, Full-stack, MLOps

### Motor de Búsqueda Híbrida Inmobiliaria — Proyecto IDT
**Período:** Mar 2023 – Ago 2023
Motor de búsqueda híbrida (Semántica + Keywords) para el sector inmobiliario. Diseño de pipelines de NLP con Haystack para procesamiento y vectorización de propiedades, framework de validación automatizada para medición de precisión del modelo, y API securizada con JWT y validación Pydantic.
- **Stack:** Python, FastAPI, Haystack, OpenSearch, Pandas, Matplotlib, JavaScript, Next.js, Docker, AWS
- **Demuestra:** NLP, Semantic Search, API Security, Data Pipeline, Cloud Deployment

---

## Roadmap de Carrera

### Fase 1 (actual): AI Backend Engineer / Applied ML Engineer
Integrar capacidades de IA en aplicaciones backend. RAG, contenedores Docker, CI/CD para ML.

### Fase 2 (1-3 años): AI Software Engineer / MLOps Engineer
Fine-tuning de modelos, agentes autónomos, Continuous Training, RL en producción.

### Fase 3 (3-5+ años): Principal AI Architect / AI Tech Lead
Arquitecturas multimodelo, gobernanza de IA, liderazgo técnico.

---

*Documento base para el RAG del portfolio. Última actualización: abril 2026.*
