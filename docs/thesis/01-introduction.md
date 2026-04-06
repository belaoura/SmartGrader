# Chapter 1: General Introduction

## 1.1 Context and Motivation

The evaluation of student performance through written examinations remains one of the most critical activities in educational institutions worldwide. In Algerian universities and secondary schools alike, instructors routinely administer paper-based examinations ranging from multiple-choice questionnaires (MCQs) to short-answer and open-ended questions. The subsequent grading of these examinations is a labour-intensive process that places a significant burden on teaching staff, particularly in large-enrolment courses where a single instructor may be responsible for evaluating hundreds of answer sheets within a constrained time frame.

Manual grading suffers from several well-documented shortcomings. First, it is inherently time-consuming: an instructor grading a thirty-question MCQ examination for a class of two hundred students must inspect and tally six thousand individual responses, a task that can easily consume an entire working day. Second, human fatigue introduces inconsistency and error. Studies in educational measurement have consistently shown that grader reliability diminishes over extended marking sessions, leading to discrepancies that can disadvantage students whose papers happen to be evaluated later in the process. Third, the lack of a standardised digital record means that grading data is difficult to aggregate, analyse, or revisit, limiting the capacity of institutions to perform systematic quality assurance on their assessment processes.

The advent of Optical Mark Recognition (OMR) technology partially addressed the first of these problems by enabling the automated reading of bubble-sheet answer forms. Commercial OMR systems such as Remark Office OMR, GradeCam, and ZipGrade have gained adoption in certain educational contexts, offering rapid processing of MCQ examinations. However, these solutions present their own limitations. Many are proprietary and carry non-trivial licensing costs that place them beyond the reach of publicly funded Algerian institutions. More critically, they are restricted to the MCQ format and offer no capability for evaluating free-text or short-answer responses, which constitute a substantial proportion of university-level assessments.

Recent advances in artificial intelligence, and in particular the emergence of Vision Language Models (VLMs), have opened new possibilities for automating the evaluation of handwritten student responses. Models such as Qwen2.5-VL and LLaVA are capable of jointly processing visual and textual information, enabling them to read handwritten text directly from scanned examination sheets and to assess the semantic correctness of student answers against a reference rubric. When combined with Retrieval-Augmented Generation (RAG) techniques, these models can progressively improve their grading accuracy by incorporating teacher corrections as few-shot learning examples.

It is within this context that the SmartGrader project was conceived: a comprehensive, open-source examination grading system that unifies MCQ scanning through computer vision with AI-assisted evaluation of short-answer questions, delivered through a modern web interface accessible to any instructor with a standard computer and a document scanner.

## 1.2 Problem Statement

The central problem addressed by this project can be formulated as follows:

> *How can we design and implement an integrated system that automates the grading of both multiple-choice and short written-answer examinations, leveraging computer vision for optical mark recognition and vision language models for handwriting recognition and semantic evaluation, while remaining deployable on modest hardware and accessible through a standard web browser?*

This problem encompasses several interrelated challenges. The system must reliably detect and interpret filled bubbles on printed answer sheets under varying scan quality and lighting conditions. It must accurately recognise handwritten student responses in multiple languages, including Arabic and French. It must evaluate the semantic correctness of free-text answers against instructor-provided model answers and grading criteria. Finally, it must present all of these capabilities through an intuitive user interface that requires no specialised technical knowledge to operate.

## 1.3 Objectives

The project pursues four principal objectives:

1. **Restructure the legacy codebase into a clean, layered architecture.** The initial prototype of SmartGrader was developed as a monolithic desktop application with tightly coupled components. The first objective is to refactor this codebase into a well-structured Flask-based backend following the Model-Service-Route pattern, with clear separation of concerns between data access, business logic, and presentation layers.

2. **Build a modern web user interface replacing the desktop application.** The second objective is to develop a responsive, accessible frontend application using React, Vite, Tailwind CSS, and the shadcn/ui component library, providing instructors with a browser-based interface for managing examinations, scanning answer sheets, and reviewing grading results.

3. **Integrate a vision language model for handwriting OCR and AI-assisted grading.** The third objective is to incorporate the Qwen2.5-VL-3B-Instruct model, quantised to 4-bit precision for deployment on consumer-grade GPUs, to perform optical character recognition on handwritten responses and to evaluate them against model answers. A RAG-based feedback loop enables the system to learn from teacher corrections over time.

4. **Produce formal academic documentation.** The fourth objective is to deliver a complete set of project documentation, including UML design diagrams, a comprehensive test suite, and this thesis document, meeting the standards expected of a final-year graduation project.

## 1.4 Methodology

The development of SmartGrader followed an incremental migration methodology, structured around four sequential sub-projects:

- **Sub-Project 1: Code Restructuring.** The monolithic legacy codebase was decomposed into a layered architecture comprising SQLAlchemy models, service modules, Flask route blueprints, and a dedicated scanner pipeline. A comprehensive test suite was established to ensure behavioural equivalence with the original system.

- **Sub-Project 2: Modern Web Interface.** A React-based single-page application was developed to replace the desktop frontend. The interface was built using Vite as the build tool, Tailwind CSS for styling, and shadcn/ui for pre-built accessible components. TanStack Query was employed for server state management, providing automatic caching and synchronisation with the backend API.

- **Sub-Project 3: AI Vision Integration.** The Qwen2.5-VL-3B-Instruct vision language model was integrated into the backend, loaded with 4-bit quantisation via the BitsAndBytes library to enable deployment on GPUs with 6--8 GB of VRAM. A two-stage pipeline was implemented: an OCR stage that extracts handwritten text from scanned images, followed by an evaluation stage that scores the extracted text against the model answer. A RAG feedback mechanism stores teacher corrections and injects them as few-shot examples in subsequent evaluations.

- **Sub-Project 4: Academic Documentation.** The present thesis document was authored, together with seven UML diagrams and a complete bibliography, following the conventions of Algerian PFE thesis formatting.

Each sub-project was developed on an isolated Git branch, with integration into the main branch occurring only after successful completion of all unit and integration tests. This incremental approach minimised regression risk and allowed each phase to build upon a stable foundation.

## 1.5 Document Organisation

The remainder of this thesis is organised as follows:

**Chapter 2: State of the Art** surveys the existing literature and commercial solutions relevant to the SmartGrader project. It reviews established OMR systems, computer vision techniques for document analysis, the emerging family of vision language models, handwriting recognition approaches, and retrieval-augmented generation. The chapter concludes with a comparative synthesis and an identification of the gaps that SmartGrader aims to fill.

**Chapter 3: Analysis and Design** presents the requirements analysis and system design. It defines the functional and non-functional requirements, describes the system architecture using UML diagrams (use case, class, sequence, entity-relationship, and deployment diagrams), details the database schema and REST API design, and specifies the AI grading pipeline.

**Chapter 4: Implementation** describes the technical realisation of the system. It covers the development environment and tools, the backend implementation (Flask application factory, SQLAlchemy models, service layer, scanner pipeline), the AI integration (model loading, prompt engineering, RAG feedback loop), and the frontend implementation (React components, state management, theming).

**Chapter 5: Testing and Results** presents the testing methodology and experimental results. It reports on the automated test suite covering 56 tests across all modules, evaluates MCQ scanning accuracy through precision and recall metrics, assesses AI grading performance against teacher-assigned scores, and analyses the impact of the RAG feedback mechanism on grading accuracy over time.

**Chapter 6: Conclusion and Perspectives** summarises the achievements of the project, acknowledges its current limitations, and proposes directions for future work, including LoRA fine-tuning, mobile application development, and support for essay-length responses.
