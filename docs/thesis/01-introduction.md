# Chapter 1: General Introduction

## 1.1 Context and Motivation

The evaluation of student performance through written examinations remains one of the most critical activities in educational institutions worldwide. In Algerian universities and secondary schools alike, instructors routinely administer paper-based examinations ranging from multiple-choice questionnaires (MCQs) to short-answer and open-ended questions. The subsequent grading of these examinations is a labour-intensive process that places a significant burden on teaching staff, particularly in large-enrolment courses where a single instructor may be responsible for evaluating hundreds of answer sheets within a constrained time frame.

Manual grading suffers from several well-documented shortcomings. First, it is inherently time-consuming: an instructor grading a thirty-question MCQ examination for a class of two hundred students must inspect and tally six thousand individual responses, a task that can easily consume an entire working day. Second, human fatigue introduces inconsistency and error. Studies in educational measurement have consistently shown that grader reliability diminishes over extended marking sessions, leading to discrepancies that can disadvantage students whose papers happen to be evaluated later in the process. Third, the lack of a standardised digital record means that grading data is difficult to aggregate, analyse, or revisit, limiting the capacity of institutions to perform systematic quality assurance on their assessment processes.

The advent of Optical Mark Recognition (OMR) technology partially addressed the first of these problems by enabling the automated reading of bubble-sheet answer forms. Commercial OMR systems such as Remark Office OMR, GradeCam, and ZipGrade have gained adoption in certain educational contexts, offering rapid processing of MCQ examinations. However, these solutions present their own limitations. Many are proprietary and carry non-trivial licensing costs that place them beyond the reach of publicly funded Algerian institutions. More critically, they are restricted to the MCQ format and offer no capability for evaluating free-text or short-answer responses, which constitute a substantial proportion of university-level assessments.

Beyond grading, the traditional model of paper-based, in-person examinations presents additional challenges as educational institutions seek to expand access and continuity of assessment. The need for simultaneous physical presence, supervised examination rooms, and manual sheet distribution creates logistical constraints that are particularly acute for large institutions or distributed student populations. Online examination platforms offer a partial solution, but widely deployed systems such as Moodle Quiz, Google Forms, and ExamSoft each present limitations in terms of academic integrity, deployment flexibility, or integration with existing institutional infrastructure.

Recent advances in artificial intelligence, and in particular the emergence of Vision Language Models (VLMs) and browser-based machine learning frameworks, have opened new possibilities for automating both the evaluation of handwritten student responses and the real-time monitoring of online examination integrity. Models such as Qwen2.5-VL and LLaVA are capable of jointly processing visual and textual information, enabling them to read handwritten text directly from scanned examination sheets and to assess the semantic correctness of student answers against a reference rubric. Simultaneously, frameworks such as TensorFlow.js enable the deployment of face detection and behaviour analysis models directly within the browser, providing a basis for non-invasive academic integrity monitoring without requiring server-side video processing.

It is within this context that the SmartGrader project was conceived: a comprehensive, open-source examination management platform that unifies MCQ scanning through computer vision, AI-assisted evaluation of short-answer questions, a fully integrated online examination engine with real-time proctoring capabilities, and flexible deployment modes including local LAN, university server, and containerised cloud environments, all delivered through a modern web interface accessible to any instructor or student with a standard browser.

## 1.2 Problem Statement

The central problem addressed by this project can be formulated as follows:

> *How can we design and implement an integrated system that automates the grading of both multiple-choice and short written-answer examinations, supports fully online examination delivery with real-time academic integrity monitoring, leverages computer vision for optical mark recognition and vision language models for handwriting recognition and semantic evaluation, and remains flexibly deployable on a range of hardware configurations from a single local machine to a university-wide server infrastructure?*

This problem encompasses several interrelated challenges. The system must reliably detect and interpret filled bubbles on printed answer sheets under varying scan quality and lighting conditions. It must accurately recognise handwritten student responses in multiple languages, including Arabic and French. It must evaluate the semantic correctness of free-text answers against instructor-provided model answers and grading criteria. It must support the delivery of online examinations with session management, timer control, and answer persistence. It must monitor student behaviour during online examinations using browser-based face detection and event tracking without requiring server-side video storage. Finally, it must present all of these capabilities through an intuitive user interface that requires no specialised technical knowledge to operate, and it must be deployable across a range of infrastructure configurations suited to the resource constraints of Algerian educational institutions.

## 1.3 Objectives

The project pursues the following principal objectives:

1. **Restructure the legacy codebase into a clean, layered architecture.** The initial prototype of SmartGrader was developed as a monolithic desktop application with tightly coupled components. The first objective is to refactor this codebase into a well-structured Flask-based backend following the Model-Service-Route pattern, with clear separation of concerns between data access, business logic, and presentation layers.

2. **Build a modern web user interface replacing the desktop application.** The second objective is to develop a responsive, accessible frontend application using React, Vite, Tailwind CSS, and the shadcn/ui component library, providing instructors with a browser-based interface for managing examinations, scanning answer sheets, reviewing grading results, and administering online examinations.

3. **Integrate a vision language model for handwriting OCR and AI-assisted grading.** The third objective is to incorporate the Qwen2.5-VL-3B-Instruct model, quantised to 4-bit precision for deployment on consumer-grade GPUs, to perform optical character recognition on handwritten responses and to evaluate them against model answers. A RAG-based feedback loop enables the system to learn from teacher corrections over time.

4. **Implement a fully online examination engine with role-based access control.** The fourth objective is to build a complete online examination subsystem comprising JWT-based authentication with teacher and student roles, student group management, exam session scheduling, a timed student-facing exam interface with answer persistence and auto-submission, and a real-time teacher monitoring dashboard.

5. **Develop a browser-based anti-cheat and proctoring system.** The fifth objective is to implement a hybrid anti-cheat system that employs TensorFlow.js and the BlazeFace model for in-browser face presence detection, browser event tracking (tab switching, fullscreen exit, copy-paste events), periodic webcam snapshot capture, and a teacher-facing proctoring dashboard that aggregates all integrity signals with warning escalation.

6. **Support flexible deployment configurations.** The sixth objective is to ensure that SmartGrader can be deployed as a single-machine development server, as a LAN-accessible institutional service (Gunicorn + Nginx), as a Docker-containerised application, and with SSL/TLS termination and hardened CORS policies appropriate for production environments.

7. **Produce formal academic documentation.** The seventh objective is to deliver a complete set of project documentation, including UML design diagrams, a comprehensive test suite, and this thesis document, meeting the standards expected of a final-year graduation project.

## 1.4 Methodology

The development of SmartGrader followed an incremental methodology, structured around four sequential phases:

- **Phase 1: Authentication and Role Management.** The foundation was extended with a JWT-based authentication system supporting teacher and student roles, barcode-based student login, and CSV bulk import of student accounts. This phase established the security perimeter and the role-based access control model upon which subsequent phases depend.

- **Phase 2: Online Examination Engine.** A complete online examination subsystem was built on top of the authenticated backend. This phase introduced student group management, exam session scheduling and assignment, a student-facing timed examination interface with persistent answer drafting and auto-submission on timer expiry, and a teacher monitoring dashboard for real-time session oversight.

- **Phase 3: Anti-Cheat and Proctoring.** A browser-native proctoring layer was integrated into the student examination interface. The ProctorEngine runs TensorFlow.js with the BlazeFace model to detect face presence at configurable intervals. Browser events including tab switching, fullscreen exit, visibility changes, and copy-paste attempts are tracked and reported. Periodic webcam snapshots are transmitted to the server and associated with the examination attempt. A warning escalation system automatically terminates the attempt after a configurable number of integrity violations. A dedicated proctoring dashboard allows teachers to review all events and snapshots for each student.

- **Phase 4: Deployment and Infrastructure.** The application was prepared for production deployment across multiple target environments: LAN mode for classroom or departmental use (Gunicorn serving the Flask application, Nginx acting as a reverse proxy), university server mode with SSL/TLS certificates and hardened CORS policies, and Docker Compose for portable containerised deployment. Environment-specific configuration, health check endpoints, and startup scripts were provided for each deployment mode.

Each phase was developed on an isolated Git branch, with integration into the main branch occurring only after successful completion of all unit and integration tests. The test suite grew from an initial 56 tests to 191 tests across all phases, providing comprehensive regression protection at each stage of development.

## 1.5 Document Organisation

The remainder of this thesis is organised as follows:

**Chapter 2: State of the Art** surveys the existing literature and commercial solutions relevant to the SmartGrader project. It reviews established OMR systems, online examination platforms, computer vision techniques for document analysis, the emerging family of vision language models, browser-based face detection frameworks, handwriting recognition approaches, JWT authentication, and retrieval-augmented generation. The chapter concludes with an expanded comparative synthesis and an identification of the gaps that SmartGrader aims to fill.

**Chapter 3: Analysis and Design** presents the requirements analysis and system design. It defines the functional and non-functional requirements for all four phases, describes the extended system architecture using UML diagrams, details the database schema including all new tables introduced for authentication, session management, and proctoring, specifies the full REST API, presents the authentication architecture with JWT flow, and describes the online examination and anti-cheat system designs.

**Chapter 4: Implementation** describes the technical realisation of the system across all four phases. It covers the development environment and tools, the backend implementation (authentication middleware, online exam engine, proctoring event service), the anti-cheat frontend implementation (ProctorEngine with BlazeFace, event tracking, snapshot capture), and the deployment configurations for each target environment.

**Chapter 5: Testing and Results** presents the testing methodology and empirical results. It reports on the automated test suite covering 191 tests across all modules, evaluates MCQ scanning accuracy, assesses AI grading performance, and reports on the online examination and proctoring subsystems including timing and performance benchmarks.

**Chapter 6: Conclusion and Perspectives** summarises the achievements of all four phases, acknowledges current limitations, and proposes directions for future work.
