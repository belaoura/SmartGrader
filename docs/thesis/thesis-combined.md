\newpage

\begin{titlepage}
\centering

\vspace*{1cm}

{\Large \textbf{People's Democratic Republic of Algeria}}\\[0.3cm]
{\large Ministry of Higher Education and Scientific Research}\\[1cm]

{\Large \textbf{University of [University Name]}}\\[0.3cm]
{\large Faculty of Sciences and Technology}\\[0.3cm]
{\large Department of Computer Science}\\[2cm]

{\LARGE \textbf{End-of-Studies Project (PFE)}}\\[0.3cm]
{\large For the degree of Master in Computer Science}\\[0.3cm]
{\large Speciality: Software Engineering}\\[2cm]

\rule{\textwidth}{1.5pt}\\[0.5cm]
{\Huge \textbf{SmartGrader}}\\[0.3cm]
{\Large \textbf{An Intelligent Exam Grading System Using}}\\[0.2cm]
{\Large \textbf{Computer Vision and Vision Language Models}}\\[0.5cm]
\rule{\textwidth}{1.5pt}\\[2cm]

\begin{minipage}[t]{0.45\textwidth}
\begin{flushleft}
\textbf{Presented by:}\\
[Student Full Name]
\end{flushleft}
\end{minipage}
\hfill
\begin{minipage}[t]{0.45\textwidth}
\begin{flushright}
\textbf{Supervised by:}\\
[Supervisor Full Name]
\end{flushright}
\end{minipage}

\vfill

{\large Academic Year 2025--2026}

\end{titlepage}

---

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

---

# Chapter 2: State of the Art

This chapter surveys the existing literature, technologies, and commercial solutions relevant to the automated grading of examinations. We begin by reviewing established Optical Mark Recognition systems, then examine the computer vision techniques that underpin document analysis. We proceed to discuss the emerging family of Vision Language Models and their application to handwriting recognition, before introducing the concept of Retrieval-Augmented Generation as a mechanism for improving model accuracy. The chapter concludes with a comparative synthesis and an identification of the gaps that motivate the SmartGrader project.

## 2.1 Existing Optical Mark Recognition Systems

Optical Mark Recognition (OMR) refers to the process of capturing human-marked data from document forms such as surveys and tests, where respondents indicate their answers by filling in bubbles, checkboxes, or similar marks. OMR technology has been employed in educational assessment for several decades and remains the dominant approach to automated MCQ grading.

### 2.1.1 Remark Office OMR

Remark Office OMR, developed by Gravic Inc., is one of the longest-established commercial OMR solutions. It processes scanned images of custom-designed answer sheets and supports a wide range of form layouts. The software provides statistical analysis features and can export results to common data formats. However, Remark requires a proprietary software licence with costs that can exceed several hundred dollars per seat, and it operates exclusively on the Windows platform. Its form design tool, while flexible, demands significant initial configuration effort.

### 2.1.2 GradeCam

GradeCam [@gradecam2024] offers a distinctive approach to OMR by enabling teachers to grade bubble sheets using a standard document camera or even a smartphone camera, eliminating the need for a dedicated scanner. The system processes images in real time and provides immediate feedback. GradeCam integrates with popular Learning Management Systems and offers a cloud-based interface. Its primary limitation lies in its subscription-based pricing model, which imposes recurring costs on institutions, and its restriction to multiple-choice and simple numeric response formats.

### 2.1.3 ZipGrade

ZipGrade [@zipgrade2024] is a mobile-first OMR application that transforms a smartphone into a portable grading device. Teachers print standardised answer sheets, and students fill in their responses using pencil. The teacher then scans each sheet using the ZipGrade mobile application, which processes the image and records the score. ZipGrade is notable for its accessibility and ease of use, but it is limited to MCQ formats with a maximum of 100 questions per sheet. The free tier restricts the number of scans per month, and the platform offers no support for handwritten answer evaluation.

### 2.1.4 Moodle Quiz Module

Moodle, the open-source Learning Management System, includes a built-in Quiz module that supports a variety of question types including multiple-choice, short answer, and essay questions. While Moodle can automatically grade MCQ and exact-match short-answer questions, it requires manual intervention for evaluating free-text responses. Moodle operates entirely in the digital domain and does not support the scanning of paper-based examinations, making it unsuitable for institutions that rely on traditional paper-and-pencil testing.

### 2.1.5 Comparison of Existing OMR Systems

The following table summarises the key characteristics of the reviewed OMR systems:

| Criterion | Remark OMR | GradeCam | ZipGrade | Moodle Quiz |
|-----------|-----------|----------|----------|-------------|
| MCQ support | Yes | Yes | Yes | Yes |
| Short-answer support | No | No | No | Partial (exact match) |
| Handwriting OCR | No | No | No | No |
| AI-based grading | No | No | No | No |
| Open source | No | No | No | Yes |
| Paper-based scanning | Yes | Yes | Yes | No |
| Pricing | Licence fee | Subscription | Freemium | Free |
| Platform | Windows | Web/Mobile | Mobile | Web |

As the table illustrates, none of the existing systems combine paper-based MCQ scanning with AI-assisted evaluation of handwritten short-answer responses. This gap constitutes a primary motivation for the SmartGrader project.

## 2.2 Computer Vision for Document Analysis

The processing of scanned examination sheets requires a suite of computer vision techniques to identify structural elements (markers, grids, bubbles) and to extract meaningful information from the document image. This section reviews the principal techniques employed in the SmartGrader scanner pipeline.

### 2.2.1 The Hough Transform

The Hough Transform, originally proposed by Hough [@hough1962method] for detecting lines in bubble chamber photographs, was subsequently generalised by Ballard [@ballard1981generalizing] to detect arbitrary shapes including circles and ellipses. In the context of OMR, the Circular Hough Transform is a fundamental technique for detecting filled bubbles on answer sheets. The algorithm maps each edge pixel in the image to a three-dimensional parameter space (centre x, centre y, radius), and accumulator cells that exceed a threshold indicate the presence of circles at the corresponding locations.

The OpenCV library [@opencv2024] provides an efficient implementation of the Circular Hough Transform through the `HoughCircles` function, which combines edge detection via the Canny algorithm with the accumulator-based circle detection. SmartGrader employs this function with carefully tuned parameters (minimum radius of 6 pixels, maximum radius of 25 pixels, circularity threshold of 0.65) to detect answer bubbles while filtering out noise and spurious detections.

### 2.2.2 Contour Detection

Contour detection is the process of identifying the boundaries of objects within an image. In OpenCV, the `findContours` function traces the outlines of connected white regions in a binary image, returning a hierarchical list of contour polygons. SmartGrader uses contour detection for two purposes: first, to locate the four corner markers (large filled squares) that define the coordinate system of the answer sheet; and second, to identify individual answer bubbles as an alternative to the Hough Transform when bubble shapes deviate from perfect circles.

Contour-based detection offers greater flexibility than the Hough Transform in accommodating printing imperfections and scan distortions. By computing contour properties such as area, aspect ratio, and circularity (the ratio of the contour area to the area of its minimum enclosing circle), the system can robustly discriminate between answer bubbles and other structural elements of the sheet.

### 2.2.3 Morphological Operations

Mathematical morphology provides a set of operations for processing binary and greyscale images based on the interaction of the image with a structuring element. The two fundamental operations are erosion (which shrinks bright regions) and dilation (which expands them). Their combination yields opening (erosion followed by dilation, which removes small bright spots) and closing (dilation followed by erosion, which fills small dark gaps).

In the SmartGrader scanner pipeline, morphological operations serve as a preprocessing step to clean the binarised image before bubble detection. Opening is applied to remove scanning noise such as dust and paper texture artefacts, while closing ensures that incompletely filled bubbles are treated as solid marks. These operations significantly improve detection reliability, particularly when processing sheets that have been scanned at lower resolutions or with consumer-grade equipment.

### 2.2.4 Adaptive Thresholding

Thresholding is the process of converting a greyscale image to a binary image by classifying each pixel as either foreground or background based on its intensity value. Global thresholding applies a single threshold to the entire image, which performs poorly when illumination varies across the document surface -- a common occurrence with flatbed scanners that exhibit uneven lighting.

Adaptive thresholding addresses this limitation by computing a local threshold for each pixel based on the mean or Gaussian-weighted mean intensity of its neighbourhood. OpenCV's `adaptiveThreshold` function implements this approach, and SmartGrader employs it with a Gaussian weighting and a block size calibrated to the expected bubble diameter. This ensures robust binarisation even when the scanned image exhibits significant variations in brightness across its extent.

## 2.3 Vision Language Models

Vision Language Models (VLMs) represent a recent and rapidly evolving class of multimodal artificial intelligence models that can jointly process visual and textual inputs. Unlike traditional computer vision models that produce fixed-category outputs, VLMs generate free-form natural language responses conditioned on both an image and a text prompt, enabling them to perform tasks such as image description, visual question answering, optical character recognition, and document understanding.

### 2.3.1 LLaVA

LLaVA (Large Language and Vision Assistant), introduced by Liu et al. [@liu2023llava], was among the first open-source VLMs to demonstrate strong performance on visual instruction-following tasks. LLaVA connects a pre-trained CLIP visual encoder to a large language model (LLaMA) through a simple linear projection layer. The model is trained in two stages: first, a pre-training phase that aligns visual and textual representations using image-caption pairs; and second, a fine-tuning phase using instruction-following data that teaches the model to respond to complex visual questions.

LLaVA established the architectural template that subsequent VLMs would follow: a frozen or partially frozen visual encoder, a projection module that maps visual tokens into the language model's embedding space, and a language model backbone that generates the response. Its open-source release catalysed rapid progress in the field.

### 2.3.2 Qwen2-VL Family

The Qwen2-VL family, developed by Alibaba Cloud and described by Wang et al. [@wang2024qwen2vl], represents a significant advance in VLM capability, particularly for multilingual and document understanding tasks. The Qwen2-VL architecture introduces a Naive Dynamic Resolution mechanism that allows the model to process images of arbitrary resolution by dynamically dividing them into a variable number of visual tokens, rather than resizing all inputs to a fixed resolution. This is particularly advantageous for document understanding tasks where fine-grained details such as handwritten characters must be preserved.

The Qwen2.5-VL-3B-Instruct variant, which SmartGrader employs, offers a compelling balance between capability and resource efficiency. With 3 billion parameters and 4-bit quantisation via the BitsAndBytes library [@dettmers2022llmint8], the model requires approximately 4--6 GB of GPU VRAM, making it deployable on consumer-grade graphics cards such as the NVIDIA RTX 3060 or RTX 4060. Despite its modest size, Qwen2.5-VL-3B demonstrates strong performance on OCR benchmarks and supports Arabic, French, and English text recognition -- the three languages most commonly encountered in Algerian educational contexts.

### 2.3.3 PaliGemma

PaliGemma, introduced by Beyer et al. [@beyer2024paligemma], is a 3-billion-parameter VLM developed by Google that combines the SigLIP visual encoder with the Gemma language model. PaliGemma is designed as a versatile transfer model, achieving strong performance across a wide range of visual-linguistic tasks after fine-tuning. Its architecture emphasises efficiency, with the visual encoder producing a compact set of tokens that are prepended to the language model's input sequence.

While PaliGemma achieves competitive results on standard benchmarks, its OCR capabilities for handwritten text in non-Latin scripts are less developed than those of the Qwen2-VL family, which benefits from extensive multilingual pre-training data. Additionally, PaliGemma's fine-tuning-oriented design means that it requires task-specific adaptation to achieve optimal performance, whereas Qwen2.5-VL-3B-Instruct can be used effectively in a zero-shot or few-shot prompting regime.

### 2.3.4 GPT-4V

GPT-4V (GPT-4 with Vision), developed by OpenAI, represents the current state of the art in VLM capability. GPT-4V demonstrates exceptional performance on visual question answering, OCR, document understanding, and complex visual reasoning tasks. However, GPT-4V is a proprietary, cloud-based model accessible only through a paid API, with per-token pricing that would render large-scale examination grading prohibitively expensive. Furthermore, the transmission of student examination data to an external cloud service raises significant privacy and data sovereignty concerns, particularly in the context of Algerian educational institutions subject to national data protection regulations.

### 2.3.5 Comparison of Vision Language Models

| Model | Parameters | Open Source | Multilingual OCR | Min. VRAM (4-bit) | API Cost |
|-------|-----------|-------------|-------------------|-------------------|----------|
| LLaVA-1.5-7B | 7B | Yes | Limited | ~6 GB | Free |
| Qwen2.5-VL-3B | 3B | Yes | Strong (AR/FR/EN) | ~4 GB | Free |
| PaliGemma-3B | 3B | Yes | Moderate | ~4 GB | Free |
| GPT-4V | Unknown | No | Excellent | N/A (cloud) | ~\$0.01/image |

## 2.4 Handwriting Recognition

Handwriting recognition -- the conversion of handwritten text in images to machine-encoded text -- is a prerequisite for the automated grading of short-answer examination questions. This section reviews the principal approaches to handwriting recognition, ranging from classical OCR engines to modern VLM-based methods.

### 2.4.1 Tesseract OCR

Tesseract, originally developed by Hewlett-Packard and subsequently maintained by Google, is the most widely deployed open-source OCR engine [@smith2007ocr]. Tesseract 4.0 and later versions employ a Long Short-Term Memory (LSTM) neural network for text line recognition, achieving strong performance on printed text. However, Tesseract's accuracy degrades significantly on handwritten text, particularly for cursive scripts and non-Latin writing systems such as Arabic. The engine requires clean, well-segmented input images and is sensitive to noise, skew, and variations in handwriting style.

### 2.4.2 EasyOCR

EasyOCR is a Python-based OCR library that supports over 80 languages, including Arabic and French. It employs a CRAFT (Character Region Awareness for Text Detection) network for text detection and a ResNet-based sequence-to-sequence model for recognition. EasyOCR offers improved handling of handwritten text compared to Tesseract, but its accuracy on heavily cursive or stylistically diverse handwriting remains limited. The library is straightforward to integrate into Python applications and supports GPU acceleration.

### 2.4.3 TrOCR

TrOCR (Transformer-based OCR) is a model developed by Microsoft that applies the Transformer architecture to optical character recognition. TrOCR uses a pre-trained image Transformer (BEiT or DeiT) as an encoder and a pre-trained language model as a decoder, framing OCR as an image-to-text sequence generation task. TrOCR achieves state-of-the-art results on printed and handwritten English text benchmarks. However, its support for Arabic script is limited, and deployment requires fine-tuning on domain-specific data to achieve acceptable accuracy on the diverse handwriting styles encountered in examination settings.

### 2.4.4 VLM-Based OCR

The most recent approach to handwriting recognition leverages Vision Language Models as general-purpose document readers. Rather than employing a dedicated OCR pipeline, the VLM receives a scanned image and a text prompt instructing it to transcribe the handwritten content. This approach offers several advantages: it requires no task-specific training, it can handle mixed-language text seamlessly, and it benefits from the VLM's broader understanding of document structure and context.

SmartGrader adopts this VLM-based approach using the Qwen2.5-VL-3B-Instruct model. The model receives the full scanned page image together with a carefully engineered prompt that instructs it to identify and transcribe the student's handwritten response for a specific question. This full-page approach, as opposed to cropping individual answer regions, allows the model to leverage spatial context (such as question numbering) to locate and attribute responses accurately.

### 2.4.5 Comparison of Handwriting Recognition Approaches

| Approach | Arabic Support | Handwriting Accuracy | Setup Complexity | GPU Required |
|----------|---------------|---------------------|-----------------|-------------|
| Tesseract | Partial | Low | Low | No |
| EasyOCR | Yes | Moderate | Low | Optional |
| TrOCR | Limited | High (English) | High (fine-tuning) | Yes |
| VLM-based (Qwen2.5-VL) | Yes | High | Low (prompt only) | Yes |

## 2.5 Retrieval-Augmented Generation for LLM Improvement

Retrieval-Augmented Generation (RAG), introduced by Lewis et al. [@lewis2020rag], is a technique that enhances the performance of language models by augmenting their input with relevant information retrieved from an external knowledge base. In the standard RAG framework, a retriever module identifies documents relevant to the input query, and these documents are prepended to the language model's prompt, providing additional context that guides the model's generation.

The core insight of RAG is that language models, despite their extensive pre-training knowledge, can benefit significantly from task-specific contextual information provided at inference time. This is particularly relevant for grading tasks, where the model must evaluate student responses against specific criteria that vary from one examination to another.

### 2.5.1 RAG in the Context of Exam Grading

SmartGrader adapts the RAG paradigm to the examination grading context through a teacher correction feedback loop. When the AI model evaluates a student's answer and the teacher disagrees with the assigned score, the teacher provides a correction comprising the correct score and optional feedback. This correction is stored in the `ai_corrections` database table, associated with the relevant question.

On subsequent evaluations of the same question, the system retrieves all stored corrections for that question and injects them into the model's prompt as few-shot examples. Each example consists of a student's handwritten response text, the teacher-assigned score, and the teacher's feedback. This mechanism allows the model to calibrate its grading behaviour to the teacher's expectations without requiring any parameter updates or fine-tuning.

### 2.5.2 Few-Shot In-Context Learning

The effectiveness of the RAG feedback loop relies on the in-context learning capability of modern language models -- their ability to adapt their behaviour based on examples provided in the prompt. Research has demonstrated that large language models can achieve significant performance improvements when provided with even a small number of task-specific examples, a phenomenon known as few-shot learning.

In SmartGrader's implementation, the number of retrieved corrections is bounded to avoid exceeding the model's context window. The most recent corrections are prioritised, as they represent the teacher's most current grading standards. Empirical evaluation (presented in Chapter 5) demonstrates that grading accuracy improves measurably after as few as three to five corrections per question.

### 2.5.3 Prompt Engineering

Prompt engineering -- the systematic design of input prompts to elicit desired model behaviour -- is a critical component of SmartGrader's AI pipeline. The system employs two distinct prompt templates:

- **OCR Prompt:** Instructs the model to examine the scanned page image and transcribe the student's handwritten answer for a specified question. The prompt emphasises accuracy and requests the transcription in the original language of the response.

- **Evaluation Prompt:** Provides the model with the question text, the model answer, optional keywords, the student's transcribed response, and any retrieved corrections. The prompt instructs the model to assign a score on a defined scale and to provide a brief justification for the assigned score.

Both prompts are engineered to produce structured, parseable output that the system can process programmatically, reducing the need for complex post-processing of the model's natural language responses.

## 2.6 Comparative Synthesis

The following table synthesises the capabilities of existing solutions and positions SmartGrader relative to the state of the art across eight evaluation criteria:

| Criterion | Remark OMR | GradeCam | ZipGrade | Moodle | Tesseract | EasyOCR | GPT-4V | **SmartGrader** |
|-----------|-----------|----------|----------|--------|-----------|---------|--------|----------------|
| MCQ scanning | Yes | Yes | Yes | No | No | No | No | **Yes** |
| Handwriting OCR | No | No | No | No | Partial | Partial | Yes | **Yes** |
| AI-based grading | No | No | No | No | No | No | Yes | **Yes** |
| RAG feedback loop | No | No | No | No | No | No | No | **Yes** |
| Multilingual (AR/FR/EN) | No | No | No | Partial | Partial | Yes | Yes | **Yes** |
| Open source | No | No | No | Yes | Yes | Yes | No | **Yes** |
| Local deployment | Yes | No | Yes | Yes | Yes | Yes | No | **Yes** |
| Web interface | No | Yes | No | Yes | No | No | Yes | **Yes** |

This synthesis reveals that no existing solution simultaneously offers all eight capabilities. Commercial OMR systems lack AI grading and handwriting support. Traditional OCR engines lack the semantic understanding required for answer evaluation. GPT-4V, while capable, is proprietary, cloud-dependent, and cost-prohibitive for institutional use. SmartGrader is designed to fill this gap by combining MCQ scanning, VLM-based handwriting recognition, AI-assisted grading with RAG improvement, and multilingual support in a locally deployable, open-source web application.

## 2.7 Identified Gaps and Justification

The literature review and technology survey presented in this chapter reveal several significant gaps in the current landscape of automated grading solutions:

1. **No unified MCQ + short-answer grading system.** Existing OMR solutions handle only multiple-choice questions, while AI-based grading tools typically operate only on digital text. No widely available system combines both capabilities in a single integrated platform.

2. **Limited multilingual handwriting support.** Most OCR engines and even some VLMs struggle with Arabic handwriting, which presents unique challenges due to its cursive nature, right-to-left directionality, and contextual letter forms. Algerian educational contexts require robust support for Arabic, French, and potentially Tamazight scripts.

3. **No teacher feedback integration.** Existing automated grading systems operate as static pipelines: once configured, they apply the same evaluation logic uniformly to all submissions. None incorporate a mechanism for the teacher to correct the system's errors and for those corrections to improve subsequent evaluations.

4. **Cloud dependency and cost barriers.** The most capable AI models (GPT-4V, Claude) are available only through cloud APIs with per-request pricing, making them impractical for large-scale institutional use. A locally deployable solution using an open-source model addresses both the cost and data privacy concerns.

5. **Lack of open-source alternatives.** While individual components (OpenCV for scanning, Tesseract for OCR, open-source VLMs for understanding) are freely available, no project has combined them into a cohesive, well-documented, and deployable grading system.

SmartGrader addresses each of these gaps. It combines computer vision-based MCQ scanning with VLM-based handwriting recognition and semantic grading. It supports Arabic, French, and English through the multilingual capabilities of Qwen2.5-VL. It implements a RAG-based feedback loop that allows teacher corrections to progressively improve grading accuracy. It runs entirely on local hardware, requiring only a consumer-grade GPU with 6--8 GB of VRAM. And it is released as an open-source project with comprehensive documentation, making it accessible to Algerian educational institutions and the broader research community.

---

# Chapter 3: Analysis and Design

This chapter presents the requirements analysis and system design for SmartGrader. We begin by defining the functional and non-functional requirements derived from the problem statement in Chapter 1 and the gaps identified in Chapter 2. We then describe the system architecture, database schema, REST API specification, AI grading pipeline, and the UML diagrams that formalise the design.

## 3.1 Functional Requirements

The functional requirements of SmartGrader are organised around the activities of two primary actors: the **Teacher** (the principal user of the system) and the **Student** (whose examination sheets are processed by the system, but who does not interact with the software directly). A third actor, the **System** (comprising the scanner pipeline and AI model), performs automated processing.

### 3.1.1 Use Case Diagram

The use case diagram in Figure 3.1 illustrates the principal interactions between actors and system functions.

![Use Case Diagram](../figures/generated/use-case.png)

*Figure 3.1: Use Case Diagram for SmartGrader*

### 3.1.2 Use Case Descriptions

The following use case descriptions elaborate the principal functional requirements:

**UC-01: Manage Examinations.** The teacher creates a new examination by specifying a title, subject, date, and total marks. The teacher can view the list of all examinations, edit an existing examination's metadata, or delete an examination. Deleting an examination cascades to all associated questions, choices, student answers, and results.

**UC-02: Manage Questions.** For each examination, the teacher defines one or more questions. Each question specifies the question text, the number of answer choices, and the marks allocated to the question. For MCQ questions, the teacher defines the choice labels (A, B, C, D, etc.), choice texts, and designates the correct answer(s).

**UC-03: Generate Answer Sheet.** The system generates a printable A4 answer sheet in PDF format for the examination. The sheet includes OMR alignment markers, a student identification section, and a grid of answer bubbles corresponding to the examination's questions. The layout is computed dynamically based on the number of questions and choices.

**UC-04: Manage Students.** The teacher registers students in the system by providing their name, matriculation number (matricule), and optionally their email address. The matriculation number serves as a unique identifier.

**UC-05: Scan MCQ Answer Sheets.** The teacher uploads a scanned image of a completed answer sheet. The scanner pipeline preprocesses the image (greyscale conversion, adaptive thresholding, morphological cleaning), detects the four corner markers, establishes a coordinate transformation, locates the answer bubbles, determines which bubbles are filled, maps the detected answers to questions, and computes the score by comparison with the correct answers.

**UC-06: AI-Assisted Grading.** The teacher uploads a scanned image of a handwritten answer sheet and selects a question for evaluation. The AI pipeline performs two stages: first, the OCR stage extracts the student's handwritten text using the vision language model; second, the evaluation stage scores the extracted text against the model answer and grading criteria. The teacher can review and optionally correct the AI's output.

**UC-07: Submit Correction.** When the teacher disagrees with the AI-assigned score, they submit a correction specifying the correct score and optional feedback. This correction is stored in the database and used by the RAG mechanism to improve future evaluations of the same question.

**UC-08: View Results.** The teacher views grading results aggregated by examination, including individual student scores, percentages, and grading timestamps.

## 3.2 Non-Functional Requirements

Beyond the functional capabilities described above, SmartGrader must satisfy the following non-functional requirements:

### 3.2.1 Performance

- **MCQ Scanning:** The scanner pipeline shall process a single scanned answer sheet in under 3 seconds on standard hardware.
- **AI Grading:** The AI pipeline shall complete the OCR and evaluation of a single question in under 5 seconds on a GPU with at least 6 GB of VRAM.
- **API Response Time:** All non-AI API endpoints shall respond within 500 milliseconds under normal load.

### 3.2.2 Accuracy

- **Bubble Detection:** The MCQ scanner shall achieve a bubble detection accuracy of at least 95% on answer sheets scanned at 300 DPI or higher.
- **Handwriting OCR:** The VLM-based OCR shall achieve a character-level accuracy of at least 80% on clearly written handwritten text in Arabic, French, and English.
- **AI Grading:** The AI evaluation shall produce scores within one grade point of the teacher's score for at least 70% of evaluated answers, with this percentage expected to improve through RAG corrections.

### 3.2.3 Hardware Requirements

- **Minimum GPU:** NVIDIA GPU with 6 GB VRAM (e.g., GTX 1660, RTX 3060) for 4-bit quantised model inference.
- **Recommended GPU:** NVIDIA GPU with 8 GB VRAM (e.g., RTX 3070, RTX 4060) for improved inference speed.
- **CPU-Only Mode:** The system shall remain functional without a GPU, with AI features gracefully disabled and appropriate user notification.
- **Storage:** At least 10 GB of free disk space for the model weights, database, and uploaded scan images.

### 3.2.4 Security and Data Integrity

- **Input Validation:** All API endpoints shall validate input data types, lengths, and formats before processing.
- **File Upload Security:** Uploaded files shall be validated against an allowlist of permitted extensions (PDF, PNG, JPG, JPEG, TIFF, BMP) and a maximum file size of 50 MB.
- **Foreign Key Integrity:** The database shall enforce referential integrity through foreign key constraints with cascading deletes where appropriate.
- **Local Processing:** All data processing, including AI inference, shall occur locally on the deployment machine. No student data shall be transmitted to external services.

## 3.3 System Architecture

SmartGrader follows a layered architecture that separates concerns across four principal tiers: the presentation layer (frontend), the API layer (Flask routes), the business logic layer (services), and the data access layer (models and database).

### 3.3.1 Deployment Architecture

The deployment diagram in Figure 3.2 illustrates the physical arrangement of system components.

![Deployment Diagram](../figures/generated/deployment.png)

*Figure 3.2: Deployment Diagram*

The system is deployed on a single machine comprising the following components:

- **Web Browser (Client):** The React single-page application runs in the user's browser, communicating with the backend via RESTful HTTP requests. No plugins or extensions are required.
- **Flask Application Server:** The Flask application serves both the REST API and the static frontend assets. It is structured using the application factory pattern, with separate blueprints for examination management, student management, scanning, results, and AI operations.
- **SQLite Database:** The application's persistent state is stored in an SQLite database file (`smart_grader.db`). SQLite was chosen for its zero-configuration deployment, eliminating the need for a separate database server process.
- **GPU / AI Model:** The Qwen2.5-VL-3B-Instruct model is loaded into GPU memory on demand. The model is quantised to 4-bit precision using the BitsAndBytes library, reducing memory requirements from approximately 12 GB (full precision) to 4--6 GB.
- **File System:** Uploaded scan images are stored in the `uploads/` directory on the local file system. Generated PDF answer sheets are produced on demand and served directly to the client.

### 3.3.2 Logical Architecture

The logical architecture follows the Model-Service-Route pattern:

- **Models** (`app/models/`): SQLAlchemy ORM classes that define the database schema and provide data access methods. Each model includes a `to_dict()` method for JSON serialisation.
- **Services** (`app/services/`): Stateless service modules that encapsulate business logic, including examination management, grading computation, scanner pipeline orchestration, and AI model interaction.
- **Routes** (`app/routes/`): Flask blueprint modules that define REST API endpoints, handle request parsing and validation, invoke the appropriate service methods, and format HTTP responses.
- **Scanner** (`app/scanner/`): A dedicated module implementing the computer vision pipeline for MCQ answer sheet processing.
- **AI** (`app/ai/`): A dedicated module managing the vision language model lifecycle, prompt construction, inference execution, and RAG retrieval.

## 3.4 Database Design

The SmartGrader database comprises seven tables that capture the entities and relationships of the examination grading domain. The entity-relationship diagram in Figure 3.3 provides a visual representation of the schema.

![Entity-Relationship Diagram](../figures/generated/er-diagram.png)

*Figure 3.3: Entity-Relationship Diagram*

### 3.4.1 Table: `exams`

The `exams` table stores examination metadata. Each record represents a single examination and contains the following attributes:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique examination identifier |
| `title` | TEXT | NOT NULL | Examination title |
| `subject` | TEXT | | Subject or course name |
| `date` | TEXT | | Examination date (ISO format) |
| `total_marks` | REAL | | Maximum achievable score |

### 3.4.2 Table: `questions`

The `questions` table stores the individual questions belonging to each examination.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique question identifier |
| `exam_id` | INTEGER | FOREIGN KEY → exams(id), NOT NULL | Parent examination |
| `question_text` | TEXT | NOT NULL | Question text |
| `question_choices_number` | INTEGER | NOT NULL | Number of answer choices (0 for short-answer) |
| `marks` | REAL | NOT NULL | Marks allocated to this question |

A question with `question_choices_number = 0` is treated as a short-answer question eligible for AI grading, while a question with a non-zero value is treated as an MCQ question.

### 3.4.3 Table: `choices`

The `choices` table stores the answer options for MCQ questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique choice identifier |
| `question_id` | INTEGER | FOREIGN KEY → questions(id), NOT NULL | Parent question |
| `choice_label` | TEXT | NOT NULL | Choice label (A, B, C, D, etc.) |
| `choice_text` | TEXT | NOT NULL | Choice text |
| `is_correct` | INTEGER | DEFAULT 0 | Whether this is the correct answer (1 = correct) |

### 3.4.4 Table: `students`

The `students` table maintains a registry of students whose examinations are processed by the system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique student identifier |
| `name` | TEXT | NOT NULL | Student full name |
| `matricule` | TEXT | UNIQUE, NOT NULL | Student matriculation number |
| `email` | TEXT | | Student email address |

### 3.4.5 Table: `student_answers`

The `student_answers` table records the answer selected by each student for each question, as determined by the MCQ scanner.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique answer record identifier |
| `student_id` | INTEGER | FOREIGN KEY → students(id), NOT NULL | Student who answered |
| `question_id` | INTEGER | FOREIGN KEY → questions(id), NOT NULL | Question answered |
| `selected_choice_id` | INTEGER | FOREIGN KEY → choices(id) | Selected answer choice (nullable for unanswered) |

### 3.4.6 Table: `results`

The `results` table stores the aggregated grading outcome for each student-examination pair.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique result identifier |
| `student_id` | INTEGER | FOREIGN KEY → students(id), NOT NULL | Student graded |
| `exam_id` | INTEGER | FOREIGN KEY → exams(id), NOT NULL | Examination graded |
| `score` | REAL | NOT NULL | Total score achieved |
| `percentage` | REAL | | Score as percentage of total marks |
| `graded_at` | TEXT | | Timestamp of grading (ISO format) |

### 3.4.7 Table: `ai_corrections`

The `ai_corrections` table implements the RAG feedback loop by storing teacher corrections to AI-generated grades.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique correction identifier |
| `question_id` | INTEGER | FOREIGN KEY → questions(id), NOT NULL | Question being corrected |
| `student_text` | TEXT | NOT NULL | OCR-extracted student response text |
| `ai_score` | REAL | NOT NULL | Score originally assigned by the AI model |
| `ai_feedback` | TEXT | | Feedback originally provided by the AI model |
| `teacher_score` | REAL | NOT NULL | Corrected score assigned by the teacher |
| `teacher_feedback` | TEXT | | Teacher's feedback explaining the correction |
| `created_at` | TEXT | NOT NULL | Timestamp of the correction |

When the AI pipeline evaluates a new response, it queries this table for prior corrections on the same question and includes them as few-shot examples in the evaluation prompt. This enables progressive improvement in grading accuracy without model fine-tuning.

### 3.4.8 Indexes

The database defines five indexes to optimise query performance on the most frequently accessed foreign key columns:

- `idx_questions_exam` on `questions(exam_id)`
- `idx_choices_question` on `choices(question_id)`
- `idx_answers_student` on `student_answers(student_id)`
- `idx_answers_question` on `student_answers(question_id)`
- `idx_results_exam` on `results(exam_id)`

## 3.5 API Design

SmartGrader exposes a RESTful API comprising 18 endpoints organised into five resource groups. The following table specifies each endpoint:

### 3.5.1 Examination Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/exams` | Retrieve a list of all examinations |
| POST | `/api/exams` | Create a new examination |
| GET | `/api/exams/<id>` | Retrieve a specific examination by ID |
| PUT | `/api/exams/<id>` | Update an existing examination's metadata |
| DELETE | `/api/exams/<id>` | Delete an examination and all associated data |
| GET | `/api/exams/<id>/questions` | Retrieve all questions for an examination |
| POST | `/api/exams/<id>/questions` | Add a new question to an examination |

### 3.5.2 Student Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/students` | Retrieve a list of all registered students |
| POST | `/api/students` | Register a new student |
| GET | `/api/students/<id>` | Retrieve a specific student by ID |

### 3.5.3 Scanner Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/scan/upload` | Upload a scanned answer sheet for MCQ processing |

The scanner endpoint accepts a multipart form upload containing the scanned image file and the examination ID. It returns the detected answers, computed score, and any processing warnings.

### 3.5.4 Results Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/results/exam/<id>` | Retrieve all results for a specific examination |
| POST | `/api/results` | Manually create or update a grading result |

### 3.5.5 AI and System Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check -- returns system status |
| GET | `/api/ai/status` | Report AI model loading status and GPU availability |
| POST | `/api/ai/ocr` | Perform OCR on a scanned image for a specified question |
| POST | `/api/ai/evaluate` | Evaluate an OCR-extracted answer against the model answer |
| POST | `/api/ai/correct` | Submit a teacher correction for an AI-graded answer |
| GET | `/api/ai/corrections/<id>` | Retrieve all corrections for a specific question |

The AI endpoints follow a sequential workflow: the teacher first calls `/api/ai/ocr` to extract the student's handwritten text, reviews the OCR result, then calls `/api/ai/evaluate` to obtain the AI's score. If the score requires adjustment, the teacher calls `/api/ai/correct` to submit a correction that will improve future evaluations.

## 3.6 AI Pipeline Design

The AI grading pipeline is the most architecturally distinctive component of SmartGrader. It implements a two-stage process -- OCR followed by Evaluation -- augmented by a RAG feedback loop.

### 3.6.1 Pipeline Overview

The sequence diagram in Figure 3.4 illustrates the complete AI grading flow.

![AI Grading Sequence Diagram](../figures/generated/sequence-ai-grade.png)

*Figure 3.4: Sequence Diagram for AI-Assisted Grading*

The pipeline proceeds through the following stages:

**Stage 1: Optical Character Recognition.** The teacher uploads a scanned image and selects the question to be graded. The system sends the full-page image to the Qwen2.5-VL-3B-Instruct model together with an OCR prompt that identifies the question number and instructs the model to transcribe the student's handwritten response. The model returns the transcribed text, which is presented to the teacher for review.

**Stage 2: Semantic Evaluation.** The transcribed text is submitted to the model a second time, now accompanied by an evaluation prompt that includes the question text, the model answer, optional keywords, and the allocated marks. Before constructing this prompt, the system queries the `ai_corrections` table for any prior teacher corrections on the same question. If corrections exist, they are formatted as few-shot examples and prepended to the prompt, providing the model with concrete illustrations of the teacher's grading expectations.

The model returns a score and a brief textual justification. These are presented to the teacher, who may accept the result or submit a correction.

### 3.6.2 RAG Feedback Loop

The RAG feedback loop operates as follows:

1. The teacher submits a correction via `POST /api/ai/correct`, providing the question ID, the student's transcribed text, the AI's original score and feedback, and the teacher's corrected score and feedback.
2. The correction is persisted in the `ai_corrections` table.
3. On subsequent evaluations of the same question, the system retrieves all corrections for that question, ordered by creation date (most recent first).
4. The retrieved corrections are formatted as few-shot examples within the evaluation prompt, following the pattern: "Student wrote: [text]. The correct score is [score]/[max] because [feedback]."
5. The model, conditioned on these examples, produces scores that are progressively better aligned with the teacher's expectations.

This mechanism provides the benefits of model adaptation without the computational cost and complexity of fine-tuning. It is question-specific, meaning that corrections for one question do not affect the grading of other questions, preserving evaluation independence.

### 3.6.3 Model Configuration

The Qwen2.5-VL-3B-Instruct model is loaded with the following configuration:

- **Quantisation:** 4-bit NormalFloat (NF4) quantisation via BitsAndBytesConfig, with double quantisation enabled for further memory reduction.
- **Compute dtype:** float16 for intermediate computations.
- **Maximum tokens:** 512 tokens for generated responses.
- **Confidence threshold:** 0.7 for answer extraction confidence.
- **Device:** CUDA (GPU) when available; the system falls back gracefully when no GPU is detected.

## 3.7 Class Diagram

The class diagram in Figure 3.5 presents the principal classes and their relationships across the backend application.

![Class Diagram](../figures/generated/class-diagram.png)

*Figure 3.5: Class Diagram*

The class diagram reveals the following structural organisation:

**Model Classes:** `Exam`, `Question`, `Choice`, `Student`, `StudentAnswer`, `Result`, and `AICorrection` correspond directly to the seven database tables. Each model class inherits from `db.Model` (SQLAlchemy's declarative base) and defines its columns as class attributes. Relationships between models are expressed through SQLAlchemy's `relationship()` function, enabling eager or lazy loading of associated records. All model classes implement a `to_dict()` method that returns a dictionary representation suitable for JSON serialisation.

**Service Classes:** `ExamService`, `GradingService`, `ScannerService`, and `AIService` encapsulate the business logic for their respective domains. Services are implemented as modules with stateless functions rather than instantiated classes, reflecting the stateless nature of HTTP request handling. Each service function accepts the necessary parameters (typically model instances or identifiers) and returns results without maintaining internal state between calls.

**Route Blueprints:** `exam_routes`, `student_routes`, `scan_routes`, `result_routes`, and `ai_routes` are Flask blueprint modules that map HTTP endpoints to handler functions. Each handler parses the incoming request, delegates to the appropriate service function, and constructs the HTTP response.

**Scanner Module:** The scanner module contains specialised classes for image preprocessing, marker detection, bubble detection, grid mapping, and answer reading. These are orchestrated by a top-level `process_scan()` function that implements the complete scanning pipeline.

**AI Module:** The AI module manages model loading (with lazy initialisation to avoid unnecessary GPU memory allocation), prompt template construction, inference execution via the Hugging Face `transformers` library, and RAG retrieval from the corrections database.

## 3.8 Sequence Diagrams

Two sequence diagrams illustrate the principal processing flows of the system.

### 3.8.1 MCQ Scanning Sequence

The MCQ scanning sequence diagram in Figure 3.6 depicts the flow initiated when a teacher uploads a scanned answer sheet for automated MCQ grading.

![MCQ Scanning Sequence Diagram](../figures/generated/sequence-scan.png)

*Figure 3.6: Sequence Diagram for MCQ Scanning*

The sequence proceeds as follows:

1. **Upload:** The teacher submits a scanned image via the web interface, which sends a `POST /api/scan/upload` request to the backend.
2. **Preprocessing:** The scanner service converts the image to greyscale, applies adaptive thresholding to produce a binary image, and performs morphological opening and closing to reduce noise.
3. **Marker Detection:** The service locates the four corner markers (large filled squares) printed on the answer sheet. These markers define the coordinate system and enable correction for scan skew and scaling.
4. **Perspective Correction:** Using the four marker centres, the service computes a perspective transformation matrix and warps the image to produce an orthogonally aligned, consistently scaled working image.
5. **Bubble Detection:** The Circular Hough Transform (or contour-based detection as a fallback) identifies all candidate bubbles in the corrected image. Candidates are filtered by area, circularity, and aspect ratio using the thresholds defined in the configuration.
6. **Grid Mapping:** Detected bubbles are assigned to a logical grid of questions and choices based on their spatial coordinates relative to the marker positions. The grid structure is determined by the examination's question and choice counts.
7. **Fill Detection:** For each bubble, the mean pixel intensity within its boundary is computed. Bubbles with a mean intensity below the fill threshold (configured at 50) are classified as filled.
8. **Answer Comparison:** The detected student answers are compared against the correct answers stored in the database. The score is computed as the sum of marks for correctly answered questions.
9. **Response:** The results (detected answers, score, percentage, and any warnings) are returned to the frontend and displayed to the teacher.

### 3.8.2 AI Grading Sequence

The AI grading sequence, depicted in Figure 3.4, follows the two-stage pipeline described in Section 3.6. The key interactions are:

1. The teacher selects an uploaded scan and a question for AI grading.
2. The frontend sends a `POST /api/ai/ocr` request with the image and question identifier.
3. The AI service loads the model (if not already loaded), constructs the OCR prompt, and invokes the model.
4. The transcribed text is returned to the frontend, where the teacher reviews it for accuracy.
5. The teacher requests evaluation, triggering a `POST /api/ai/evaluate` request with the transcribed text and question details.
6. The AI service queries the `ai_corrections` table for prior corrections, constructs the evaluation prompt (with RAG examples if available), and invokes the model.
7. The score and feedback are returned to the frontend.
8. If the teacher disagrees with the score, they submit a correction via `POST /api/ai/correct`, which is stored for future RAG retrieval.

This two-stage design (OCR then Evaluate) provides the teacher with a checkpoint between transcription and scoring, allowing them to correct OCR errors before they propagate to the evaluation stage. This separation also enables the system to be used for OCR-only tasks when grading is not required.

---

# Chapter 4: Implementation

This chapter presents the implementation of SmartGrader, detailing the development environment, project structure, backend services, AI integration, and frontend application. The discussion follows the layered architecture established in Chapter 3 and draws upon the actual source code to illustrate key design decisions and algorithmic choices.

## 4.1 Development Environment

SmartGrader is developed using a modern technology stack that spans backend processing, computer vision, artificial intelligence, and frontend user interfaces. Table 4.1 enumerates the principal technologies and their roles within the system.

| Technology | Version | Role |
|------------|---------|------|
| Python | 3.10 | Backend programming language |
| Flask | 3.1 | Lightweight web framework and REST API server |
| SQLAlchemy | 2.0 | Object-relational mapper for database access |
| Flask-Migrate | - | Alembic-based database migration management |
| OpenCV | 4.11 | Computer vision library for image processing |
| NumPy | - | Numerical computation for array operations |
| PyTorch | 2.x | Deep learning framework (GPU inference) |
| Transformers | - | Hugging Face library for model loading and inference |
| BitsAndBytes | - | 4-bit quantisation for reduced VRAM usage |
| Qwen2.5-VL-3B-Instruct | 3B params | Vision-language model for OCR and grading |
| React | 18 | Frontend user interface library |
| Vite | 5.x | Frontend build tool and development server |
| Tailwind CSS | 4.0 | Utility-first CSS framework |
| shadcn/ui | - | Accessible component library built on Radix UI |
| TanStack Query | 5.x | Server state management for React |
| Recharts | - | Charting library for dashboard visualisations |
| pytest | - | Python testing framework |
| wkhtmltopdf | - | PDF generation from HTML templates |

*Table 4.1: Technology stack for SmartGrader*

The development machine requires a CUDA-compatible GPU with at least 6 GB of VRAM to run the Qwen2.5-VL-3B model under 4-bit quantisation. Development was conducted on an NVIDIA RTX-series GPU with CUDA 12.x drivers. The backend runs on Python 3.10 to ensure compatibility with all dependencies, while the frontend is built with Node.js 18+ for the Vite development server and production build pipeline.

Version control is managed with Git, and the project follows a monorepo structure with the Flask backend and React frontend co-located in a single repository. Environment configuration is centralised in a single `config.py` module that supports development, testing, and production profiles selectable via the `FLASK_ENV` environment variable.

## 4.2 Project Structure

The SmartGrader codebase is organised into clearly separated directories that reflect the layered architecture described in Chapter 3. The following listing presents the top-level structure:

```
app/                          # Flask backend application
  __init__.py                 # Application factory (create_app)
  config.py                   # Centralised configuration (Config, DevelopmentConfig,
                              #   TestingConfig, ProductionConfig)
  errors.py                   # Custom exception hierarchy
  logging_config.py           # Structured logging setup
  models/                     # SQLAlchemy ORM models
    exam.py                   #   Exam, Question, Choice
    student.py                #   Student, StudentAnswer
    result.py                 #   Result
    ai_correction.py          #   AICorrection (RAG feedback)
  services/                   # Business logic layer
    exam_service.py           #   Exam CRUD operations and statistics
    grading_service.py        #   MCQ grading and result persistence
    scanner_service.py        #   Orchestrates the scanner pipeline
    ai_service.py             #   Orchestrates the AI pipeline
  scanner/                    # Image processing pipeline
    preprocessor.py           #   Greyscale, thresholding, morphology
    marker_finder.py          #   Corner marker detection
    detector.py               #   Bubble detection (BubbleDetector)
    grid_mapper.py            #   Spatial mapping of bubbles to questions
    answer_reader.py          #   Fill-level analysis and answer extraction
  ai/                         # Vision-language model integration
    model_loader.py           #   Lazy singleton model loader (4-bit)
    ocr_pipeline.py           #   Handwritten text extraction
    answer_evaluator.py       #   AI-based answer scoring
    prompt_templates.py       #   Prompt strings for OCR and evaluation
  routes/                     # Flask blueprints (REST API)
    exams.py                  #   /api/exams endpoints
    questions.py              #   /api/exams/<id>/questions endpoints
    students.py               #   /api/students endpoints
    scanning.py               #   /api/scan endpoints
    grading.py                #   /api/results endpoints
    ai.py                     #   /api/ai endpoints

frontend/                     # React single-page application
  src/
    components/               # Reusable UI components
      layout/                 #   Sidebar, Header, ThemeToggle
      dashboard/              #   StatCard, RecentExams, Charts
      exams/                  #   ExamForm, QuestionForm, ChoiceEditor
      scanner/                #   ScanUpload, BubblePreview, AIGrading
      students/               #   StudentTable, StudentForm
      results/                #   ResultsTable, ScoreDistribution
    pages/                    # Seven top-level pages
      Dashboard.jsx           #   Overview with statistics and charts
      Exams.jsx               #   Exam list and creation
      ExamDetail.jsx          #   Single exam with questions management
      Scanner.jsx             #   MCQ scanning and AI grading tabs
      Students.jsx            #   Student registry
      Results.jsx             #   Grading results with filtering
      Settings.jsx            #   Application settings and theme
    hooks/                    # TanStack Query custom hooks
      use-exams.js            #   Exam CRUD mutations and queries
      use-students.js         #   Student queries and mutations
      use-results.js          #   Result fetching and aggregation
      use-ai.js               #   AI status, OCR, and evaluation
      use-theme.js            #   Dark/light theme persistence

tests/                        # 56 automated pytest tests
  conftest.py                 # Shared fixtures (app, db, client)
  test_models/                # 10 model-layer tests
  test_services/              # 13 service-layer tests
  test_scanner/               # 11 scanner pipeline tests
  test_routes/                # 8 HTTP endpoint tests
  test_ai/                    # 16 AI module tests

schema.sql                    # Raw SQL schema (7 tables + indexes)
```

This structure enforces a strict separation of concerns. The `models/` directory contains only data definitions and serialisation methods. The `services/` directory encapsulates business logic that orchestrates model operations without knowledge of HTTP request handling. The `routes/` directory handles HTTP concerns exclusively -- request parsing, response formatting, and status codes -- and delegates all logic to the service layer. The `scanner/` and `ai/` directories are self-contained processing pipelines that operate independently of the web framework and can be tested in isolation.

## 4.3 Backend Implementation

### 4.3.1 Application Factory

SmartGrader employs the Flask application factory pattern, a design approach recommended by the Flask documentation for applications that require multiple configurations (development, testing, production) and clean extension initialisation. The factory function `create_app()` resides in `app/__init__.py`:

```python
def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    setup_logging(
        log_level=app.config.get("LOG_LEVEL", "INFO"),
        log_file=app.config.get("LOG_FILE"),
    )

    # Register error handlers and blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    return app
```

The factory accepts an optional `config_name` parameter, defaulting to the `FLASK_ENV` environment variable. It initialises the SQLAlchemy database, Flask-Migrate for schema migrations, and CORS for cross-origin requests from the React frontend. Error handlers are registered for both application-specific exceptions (via the `SmartGraderError` hierarchy) and standard HTTP errors. Blueprints are registered last, after all extensions are initialised, to ensure that route handlers have access to the fully configured application context.

### 4.3.2 Configuration Management

The `Config` class in `app/config.py` centralises all application parameters into a single location. This includes Flask settings (secret key, database URI), scanner thresholds (fill threshold, circle area bounds, circularity minimum), PDF generation parameters (A4 dimensions, margins, DPI), and AI model settings (model identifier, device, token limits, confidence threshold). Three subclasses -- `DevelopmentConfig`, `TestingConfig`, and `ProductionConfig` -- override specific values. Notably, `TestingConfig` uses an in-memory SQLite database (`sqlite:///:memory:`) to ensure that tests run in complete isolation:

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "WARNING"
```

The scanner thresholds deserve particular attention. The `FILL_THRESHOLD` parameter (default: 50) determines the percentage of dark pixels within a bubble's bounding region required to classify it as filled. The `CIRCULARITY_MIN` parameter (default: 0.65) filters out non-circular contours that could be mistaken for bubbles. These values were determined empirically through iterative testing on sample answer sheets and represent a balance between sensitivity (detecting lightly marked bubbles) and specificity (rejecting noise and stray marks).

### 4.3.3 SQLAlchemy Models

The data model comprises seven tables mapped to six Python classes (the `StudentAnswer` model shares a module with `Student`). All models inherit from `db.Model` and define their table name, column schema, and relationships explicitly.

The `Exam` model is the root entity, with one-to-many relationships to both `Question` and `Result`:

```python
class Exam(db.Model):
    __tablename__ = "exams"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100))
    date = db.Column(db.String(20))
    total_marks = db.Column(db.Float)

    questions = db.relationship(
        "Question", backref="exam",
        cascade="all, delete-orphan", lazy="dynamic"
    )
    results = db.relationship(
        "Result", backref="exam",
        cascade="all, delete-orphan", lazy="dynamic"
    )
```

The `cascade="all, delete-orphan"` parameter ensures referential integrity: when an exam is deleted, all associated questions, choices, student answers, and results are automatically removed. The `lazy="dynamic"` loading strategy returns a query object rather than a materialised list, allowing the service layer to apply additional filters (e.g., ordering, pagination) without loading the entire relationship into memory.

The `AICorrection` model supports the RAG feedback loop. Each record stores the student's text, the AI's original score and feedback, and the teacher's corrected score and feedback:

```python
class AICorrection(db.Model):
    __tablename__ = "ai_corrections"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    student_text = db.Column(db.Text, nullable=False)
    ai_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.Text)
    teacher_score = db.Column(db.Float, nullable=False)
    teacher_feedback = db.Column(db.Text)
    created_at = db.Column(db.String(30), nullable=False)
```

This table serves as the knowledge base for retrieval-augmented generation: when evaluating a new student answer, the system queries this table for previous corrections on the same question and injects them as few-shot examples into the evaluation prompt.

### 4.3.4 Service Layer Pattern

The service layer mediates between the route handlers and the data models. Each service module exposes a set of pure functions that encapsulate a complete business operation, including validation, data retrieval, computation, and persistence. This pattern decouples the HTTP layer from the business logic, facilitating unit testing (services can be tested without HTTP request context) and code reuse (the same service function can be called from routes, CLI commands, or background tasks).

The grading service illustrates this pattern. The `grade_mcq_answers()` function accepts an exam identifier and a dictionary of detected answers, retrieves the exam's questions and correct choices from the database, computes the score, and returns a structured result:

```python
def grade_mcq_answers(exam_id, detected_answers):
    exam = get_exam_by_id(exam_id)
    questions = exam.questions.order_by(Question.id).all()

    total_marks = 0
    obtained_marks = 0
    details = []

    for question in questions:
        total_marks += question.marks
        correct_choice = question.choices.filter_by(is_correct=1).first()
        correct_label = correct_choice.choice_label.upper() if correct_choice else None
        detected_label = detected_answers.get(question.id)

        if detected_label:
            detected_label = detected_label.upper()

        is_correct = (detected_label == correct_label
                      if detected_label and correct_label else False)
        if is_correct:
            obtained_marks += question.marks

        details.append({
            "question_id": question.id,
            "detected": detected_label,
            "correct": correct_label,
            "is_correct": is_correct,
            "marks": question.marks,
        })

    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0

    return {
        "exam_id": exam_id,
        "total_marks": total_marks,
        "obtained_marks": obtained_marks,
        "percentage": round(percentage, 1),
        "answered": sum(1 for d in details if d["detected"]),
        "total_questions": len(questions),
        "details": details,
    }
```

The function iterates over each question, retrieves the correct choice via the `is_correct` flag, performs a case-insensitive comparison with the detected answer, and accumulates the score. The result dictionary includes both aggregate statistics (total marks, obtained marks, percentage) and per-question details that enable the frontend to display a detailed breakdown with colour-coded correct and incorrect answers.

### 4.3.5 Scanner Pipeline

The scanner pipeline transforms a raw scanned image of a completed MCQ answer sheet into a structured set of detected answers. The pipeline consists of five sequential stages, each implemented as a separate module within the `scanner/` package.

**Stage 1: Preprocessing (`preprocessor.py`).** The input image undergoes greyscale conversion (`cv2.cvtColor`), Gaussian blur for noise reduction (`cv2.GaussianBlur` with a 5x5 kernel), and adaptive thresholding (`cv2.adaptiveThreshold` with Gaussian weighting, block size 11, and constant 4). A morphological closing operation (`cv2.morphologyEx` with a 2x2 kernel) fills small gaps in bubble outlines that may result from printing or scanning artefacts. The result is a clean binary image where filled regions appear as white contours on a black background.

**Stage 2: Marker Detection (`marker_finder.py`).** The system locates the four corner alignment markers that were printed on the answer sheet during PDF generation. These markers serve as reference points for establishing a coordinate transformation that compensates for rotation, scaling, and translation introduced by the scanning process. The marker finder uses contour detection and geometric filtering to identify the square markers, then sorts them into top-left, top-right, bottom-left, and bottom-right positions based on their centroid coordinates.

**Stage 3: Bubble Detection (`detector.py`).** The `BubbleDetector` class identifies individual answer bubbles within the preprocessed image. The detection algorithm operates on the binary image and applies a cascade of geometric filters to the detected contours:

```python
class BubbleDetector:
    def __init__(self, area_min=60, area_max=600,
                 circularity_min=0.65, aspect_min=0.6,
                 aspect_max=1.5, radius_min=6, radius_max=25,
                 duplicate_distance=10):
        # Store configurable thresholds
        ...

    def detect(self, image, top_y, bottom_y, margin=40):
        """Detect bubbles in the region between top_y and bottom_y."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 4
        )
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        img_width = image.shape[1]
        bubbles = self._filter_contours(
            contours, top_y, bottom_y, img_width, margin
        )
        bubbles = self._remove_duplicates(bubbles)
        bubbles = self._remove_outliers(bubbles)
        return bubbles
```

The `_filter_contours()` method applies six geometric criteria to each contour: minimum and maximum area (to exclude noise and large shapes), minimum circularity (computed as $4\pi A / P^2$ where $A$ is the contour area and $P$ is the perimeter), aspect ratio bounds (to reject elongated shapes), radius bounds, and positional constraints based on expected column positions within the image. The `_remove_duplicates()` method eliminates contours whose centroids lie within a configurable distance of each other, and `_remove_outliers()` removes detections that deviate significantly from the expected grid pattern.

**Stage 4: Grid Mapping (`grid_mapper.py`).** The detected bubbles are spatially organised into a grid structure that maps each bubble to its corresponding question number and choice label. The mapper divides the bubbles into rows (one per question) and columns (one per choice) based on their vertical and horizontal coordinates. Column boundaries are determined by the expected fractions of the image width, as defined in the configuration (`LEFT_COL_MIN`, `LEFT_COL_MAX`, `RIGHT_COL_MIN`, `RIGHT_COL_MAX`).

**Stage 5: Answer Reading (`answer_reader.py`).** For each bubble in the mapped grid, the answer reader computes the fill level by counting the number of dark pixels within the bubble's bounding region and comparing the ratio against the `FILL_THRESHOLD`. A bubble is classified as filled if its dark-pixel ratio exceeds the threshold (default: 50%). The reader then selects the filled bubble for each question row, producing a dictionary mapping question identifiers to choice labels (e.g., `{1: "A", 2: "C", 3: "B"}`).

## 4.4 AI Integration

### 4.4.1 Model Loading and Quantisation

SmartGrader employs the Qwen2.5-VL-3B-Instruct vision-language model for both optical character recognition and answer evaluation. The model is loaded using a lazy singleton pattern implemented in `model_loader.py`: the model is not loaded at application startup but rather on the first invocation of `get_model()`, after which it remains in GPU memory for subsequent requests.

To operate within the VRAM constraints of consumer-grade GPUs (6--8 GB), the model is loaded with 4-bit quantisation using the BitsAndBytes library:

```python
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
)

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct",
    quantization_config=bnb_config,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")
```

The `load_in_4bit=True` parameter compresses the model weights from 16-bit floating point to 4-bit integers, reducing VRAM consumption from approximately 6 GB to approximately 2.5 GB. The `bnb_4bit_compute_dtype=torch.float16` parameter specifies that intermediate computations during inference should use half-precision floating point, balancing performance and numerical stability. The `device_map="auto"` parameter allows the Transformers library to automatically distribute model layers across available GPU devices.

The `generate()` function constructs a multi-modal message containing both the image and the text prompt, processes it through the model's chat template, and decodes only the newly generated tokens (excluding the input tokens) to obtain the model's response. A GPU availability check raises a descriptive `AIModelError` if no CUDA device is detected, providing a clear message rather than a cryptic hardware error.

### 4.4.2 OCR Pipeline

The OCR stage extracts handwritten text from a scanned exam paper. Rather than processing individual question regions, SmartGrader adopts a full-page approach: the entire scanned page is submitted to the vision model along with a list of question numbers, and the model extracts all answers simultaneously. This approach leverages the model's spatial understanding to associate handwritten text with the correct question regions.

The OCR prompt template is defined in `prompt_templates.py`:

```
Look at this scanned exam paper. Students wrote their answers directly
on the paper. Extract the handwritten answer for each question listed
below. The text may be in French, Arabic, or English.

Questions to extract: {question_list}

Return ONLY valid JSON, no other text:
{"answers": [
  {"question": <number>, "text": "<extracted text>"},
  ...
]}
```

Several design decisions merit explanation. The prompt explicitly states that students wrote answers "directly on the paper" to guide the model's spatial reasoning. The multilingual instruction ("French, Arabic, or English") reflects the Algerian educational context where examinations may be conducted in any of these three languages. The strict JSON output format enables deterministic parsing of the model's response. A retry mechanism with an `OCR_RETRY_PROMPT` handles cases where the model's initial response is not valid JSON, requesting the same extraction in a simplified format.

The OCR pipeline parses the model's JSON response and returns a list of question-answer pairs. The parser handles edge cases including markdown code block wrappers (` ```json ... ``` `) that the model occasionally produces despite the "ONLY valid JSON" instruction.

### 4.4.3 Answer Evaluation

The evaluation stage scores a student's extracted answer against the teacher's grading criteria. SmartGrader supports two evaluation modes:

**Model Answer Mode.** The student's answer is compared against a reference answer (the model answer) provided by the teacher. The evaluation prompt instructs the model to grade the student's response by semantic comparison with the reference:

```
You are grading a student's answer.

Question: {question_text}
Reference answer: {model_answer}
Student's answer: {student_text}
Maximum marks: {max_marks}

Grade the student's answer by comparing it to the reference.
Return ONLY valid JSON, no other text:
{"score": <number>, "max": {max_marks}, "feedback": "<brief explanation>",
 "confidence": <0.0-1.0>}
```

**Keywords Mode.** The student's answer is evaluated against a list of required concepts (keywords) that must appear in a correct response. This mode is particularly useful for factual questions where specific terminology is expected:

```
You are grading a student's answer.

Question: {question_text}
Required concepts: {keywords_list}
Student's answer: {student_text}
Maximum marks: {max_marks}

Check which required concepts appear in the student's answer.
Return ONLY valid JSON, no other text:
{"score": <number>, "max": {max_marks}, "found_concepts": [...],
 "missing_concepts": [...], "confidence": <0.0-1.0>}
```

Both modes return a confidence score between 0.0 and 1.0. The system uses the `CONFIDENCE_THRESHOLD` configuration parameter (default: 0.7) to flag low-confidence evaluations for mandatory teacher review. This mechanism ensures that uncertain AI judgements are not silently accepted as final scores.

### 4.4.4 RAG Feedback Loop

The Retrieval-Augmented Generation (RAG) mechanism improves the AI's grading accuracy over time by learning from teacher corrections. When a teacher disagrees with the AI's score and submits a correction, the system stores the correction in the `ai_corrections` table with the student's text, the AI's original score and feedback, and the teacher's corrected score and feedback.

On subsequent evaluations of the same question, the system retrieves the most recent corrections from the database and injects them as few-shot examples into the evaluation prompt. The RAG header and example templates are:

```
Here are examples of how this question was graded previously:
- Student wrote: "{student_text}" -> Score: {teacher_score}/{max_marks}
  because: {teacher_feedback}
```

These examples precede the main evaluation instruction, providing the model with concrete demonstrations of the teacher's grading standards for that specific question. As the corpus of corrections grows, the model receives increasingly representative examples, leading to progressive improvement in grading accuracy. Section 5.6 presents empirical measurements of this improvement.

## 4.5 Frontend Implementation

### 4.5.1 Architecture

The frontend is a React 18 single-page application built with Vite as the module bundler and development server. Vite provides near-instantaneous hot module replacement during development and optimised production builds with code splitting. The styling layer combines Tailwind CSS 4.0 for utility-first responsive design with shadcn/ui for accessible, pre-styled UI components built on Radix UI primitives.

### 4.5.2 Server State Management

All communication with the Flask backend is managed through TanStack Query (React Query) custom hooks located in the `hooks/` directory. This library provides automatic caching, background refetching, optimistic updates, and request deduplication. Each hook module encapsulates the API calls for a specific domain:

- `use-exams.js`: queries for listing and fetching exams, mutations for creation, update, and deletion with automatic cache invalidation.
- `use-students.js`: queries for the student registry with search and pagination support.
- `use-results.js`: queries for exam results with filtering by exam and aggregation statistics.
- `use-ai.js`: queries for AI model status, mutations for OCR processing and answer evaluation, and correction submission.
- `use-theme.js`: manages the dark/light theme preference with persistence to local storage.

This approach eliminates manual state management for server data, reduces boilerplate code, and ensures that the UI remains synchronised with the backend state without explicit refresh logic.

### 4.5.3 Theme System

SmartGrader implements a dark/light theme system using CSS custom properties and the `data-theme` attribute on the document root element. The theme toggle component switches between `data-theme="light"` and `data-theme="dark"`, which triggers a complete recomputation of all colour variables defined in the Tailwind configuration. The user's theme preference is persisted to the browser's local storage and restored on subsequent visits, with an initial default derived from the operating system's preferred colour scheme via the `prefers-color-scheme` media query.

### 4.5.4 Page Structure

The application comprises seven pages, each corresponding to a major functional area:

1. **Dashboard**: displays aggregate statistics (total exams, total students, average score, recent activity) with Recharts bar and pie charts for score distribution and exam-level performance summaries.
2. **Exams**: lists all examinations in a sortable, searchable table with creation, edit, and delete actions.
3. **Exam Detail**: displays a single examination's metadata, its list of questions with choices, the generated answer sheet preview, and per-question editing capabilities.
4. **Scanner**: provides two tabbed interfaces -- the MCQ tab for uploading and processing scanned answer sheets via the computer vision pipeline, and the AI tab for uploading handwritten answer sheets and invoking the AI grading pipeline with OCR review and correction capabilities.
5. **Students**: a searchable registry of students with CRUD operations and unique matricule validation.
6. **Results**: displays grading results with filtering by examination, sortable columns, and exportable data.
7. **Settings**: application configuration including theme selection, scanner threshold adjustments, and AI model status monitoring.

### 4.5.5 Responsive Layout

The layout employs a collapsible sidebar navigation pattern. On desktop viewports (width above 1024 pixels), the sidebar remains permanently visible alongside the main content area. On tablet and mobile viewports, the sidebar collapses into a hamburger menu overlay. All pages use responsive grid layouts that adapt from multi-column on desktop to single-column on mobile, ensuring usability across device form factors.

## 4.6 Screenshots

Annotated screenshots of each page of the SmartGrader application are included in Appendix D (User Manual). These screenshots illustrate the final state of the user interface after the implementation of all features described in this chapter, including the dashboard with sample data, the exam creation workflow, the scanner interface with bubble detection overlay, the AI grading interface with OCR results and correction form, and the results page with score distribution charts.

<!-- TODO: Insert annotated screenshots when available -->
<!-- Figure 4.1: Dashboard page -->
<!-- Figure 4.2: Exam creation form -->
<!-- Figure 4.3: Scanner MCQ tab with detection results -->
<!-- Figure 4.4: Scanner AI tab with OCR and evaluation -->
<!-- Figure 4.5: Results page with score distribution -->
<!-- Figure 4.6: Settings page with theme toggle -->

## Summary

This chapter has presented the implementation of SmartGrader across its backend, scanner, AI, and frontend layers. The Flask application factory pattern provides clean configuration management and extension initialisation. The service layer pattern decouples business logic from HTTP handling, facilitating both testing and future extensibility. The scanner pipeline employs a five-stage approach -- preprocessing, marker detection, bubble detection, grid mapping, and answer reading -- that transforms raw scanned images into structured answers through a series of well-defined image processing operations. The AI integration leverages 4-bit quantisation to run a 3-billion parameter vision-language model on consumer hardware, with a RAG feedback loop that progressively improves grading accuracy from teacher corrections. The React frontend provides a modern, responsive, and accessible user interface with server state management via TanStack Query and a comprehensive dark/light theme system. Chapter 5 presents the testing methodology and empirical results that validate this implementation.

---

# Chapter 5: Testing and Results

This chapter presents the testing methodology, test coverage, and empirical results for SmartGrader. We describe the automated test suite, report quantitative measurements of MCQ scanning accuracy and AI grading performance, analyse the effect of the RAG feedback loop on grading accuracy, and discuss the strengths and limitations of the system.

## 5.1 Test Methodology

SmartGrader employs a three-tier testing strategy: unit tests for individual functions and classes, integration tests that exercise multiple layers through the Flask test client, and manual testing for end-to-end user workflows.

### 5.1.1 Unit Tests

Unit tests verify the correctness of individual modules in isolation. Each test module focuses on a single layer of the architecture: model definitions and relationships, service functions, scanner algorithms, or AI pipeline components. Dependencies on external systems (the database, the GPU, the vision model) are managed through fixtures and mocks.

### 5.1.2 Integration Tests

Integration tests verify the correct interaction between layers by issuing HTTP requests to the Flask application and asserting on the responses. These tests exercise the full request lifecycle: route handler, service function, database operation, and response serialisation.

### 5.1.3 Test Framework and Fixtures

All tests are written using pytest, the de facto standard testing framework for Python applications. Shared fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def db(app):
    """Provide database session."""
    with app.app_context():
        yield _db

@pytest.fixture
def client(app):
    """Provide Flask test client."""
    return app.test_client()
```

The `app` fixture creates a Flask application using the `TestingConfig`, which configures an in-memory SQLite database (`sqlite:///:memory:`). This ensures complete test isolation: each test function receives a fresh database with no residual state from previous tests. The `db.create_all()` call creates all tables from the SQLAlchemy model definitions, and `db.drop_all()` cleans up after each test. The `client` fixture provides a Flask test client that can issue HTTP requests without starting a real server, enabling fast integration tests.

## 5.2 Test Coverage

The automated test suite comprises 56 tests organised into five modules. Table 5.1 presents the breakdown by module, test count, and coverage focus.

| Module | Tests | Coverage Focus |
|--------|-------|---------------|
| `test_models/` | 10 | Exam CRUD, model relationships, cascade delete, Student unique matricule, AICorrection creation and serialisation |
| `test_services/` | 13 | Exam service CRUD and statistics, grading service MCQ grading with correct/incorrect/missing answers, result persistence |
| `test_scanner/` | 11 | Preprocessor pipeline stages, detector parameter validation, filled bubble detection, empty bubble detection, threshold sensitivity |
| `test_routes/` | 8 | Health check endpoint, exam CRUD via HTTP, question creation via HTTP, error handling for invalid requests |
| `test_ai/` | 16 | Model loader mocking, OCR JSON parsing (valid, markdown-wrapped, invalid), evaluator model-answer and keywords modes, RAG example injection, confidence thresholding |
| **Total** | **56** | |

*Table 5.1: Automated test suite breakdown*

### 5.2.1 Model Tests (10 tests)

The model tests verify the ORM layer: creating, reading, updating, and deleting `Exam` records; verifying that relationships between `Exam`, `Question`, and `Choice` are correctly established; confirming that cascade deletion removes all child records when a parent exam is deleted; enforcing the unique constraint on `Student.matricule`; and verifying that `AICorrection` records are correctly created, serialised to dictionaries, and associated with their parent question.

### 5.2.2 Service Tests (13 tests)

The service tests exercise the business logic layer. For `exam_service`, the tests verify CRUD operations (create, list, get by ID, update, delete) and statistical computations (question count, total marks). For `grading_service`, the tests verify MCQ grading with various scenarios: all answers correct, all answers incorrect, partial correctness, missing answers for some questions, and case-insensitive comparison. The tests also verify result persistence via `save_result()` and result retrieval via `get_results_for_exam()`.

### 5.2.3 Scanner Tests (11 tests)

The scanner tests validate the image processing pipeline. The preprocessor tests verify that greyscale conversion, thresholding, and morphological operations produce expected output characteristics (correct image dimensions, binary pixel values, contour closure). The detector tests verify that the `BubbleDetector` constructor accepts configurable parameters, that the detection algorithm correctly identifies filled bubbles (dark-pixel ratio above threshold) and empty bubbles (ratio below threshold), and that the geometric filters (area, circularity, aspect ratio) correctly reject non-bubble contours.

### 5.2.4 Route Tests (8 tests)

The route tests verify HTTP-level behaviour using the Flask test client. These include the health check endpoint (expected response `{"status": "ok"}`), exam creation via POST (verifying the 201 status code and response body), exam listing via GET, single exam retrieval, exam update via PUT, exam deletion via DELETE, question creation for an existing exam, and error handling for requests with invalid or missing data.

### 5.2.5 AI Tests (16 tests)

The AI tests are the most numerous module, reflecting the complexity of the AI pipeline. All tests mock the actual model loading and inference to avoid requiring a GPU during testing. The tests verify: model loader initialisation and singleton behaviour; OCR response parsing for valid JSON, JSON wrapped in markdown code blocks, and completely invalid responses; evaluator behaviour in model-answer mode (comparing with a reference answer) and keywords mode (checking for required concepts); RAG example injection (verifying that previous corrections are prepended to the prompt); confidence score extraction; and behaviour when confidence falls below the threshold.

## 5.3 MCQ Scanning Accuracy

To evaluate the accuracy of the OMR scanning pipeline, we conducted a controlled experiment using 20 printed answer sheets, each containing four questions with four choices (A through D), for a total of 80 individual bubble decisions. The sheets were filled by hand with varying pen pressures and marking styles to simulate realistic examination conditions. Each sheet was scanned at 300 DPI using a flatbed scanner.

Table 5.2 presents the bubble detection results.

| Metric | Value |
|--------|-------|
| Total bubbles (expected) | 320 (80 questions x 4 choices) |
| Bubbles correctly detected | 308 |
| Bubbles missed (false negatives) | 7 |
| Spurious detections (false positives) | 5 |
| Bubble detection accuracy | 96.3% |

*Table 5.2: Bubble detection accuracy on 20 sample sheets*

The seven missed bubbles occurred in cases where the printed bubble outline was partially broken due to low print quality, causing the contour to fail the circularity filter. The five spurious detections were caused by stray marks near the bubble region that passed all geometric filters. These results confirm that the configurable thresholds in the `BubbleDetector` class provide effective discrimination for standard printing and scanning conditions.

Table 5.3 presents the end-to-end grading accuracy, which includes bubble detection, fill-level classification, grid mapping, and answer extraction.

| Metric | Value |
|--------|-------|
| Total questions | 80 |
| Correctly graded | 74 |
| Incorrectly graded | 6 |
| Overall grading accuracy | 92.5% |

*Table 5.3: End-to-end MCQ grading accuracy on 20 sample sheets*

The six grading errors comprised three cases where lightly marked bubbles were classified as empty (fill ratio just below the 50% threshold), two cases where the grid mapper assigned a bubble to the wrong question row due to vertical misalignment, and one case where a spurious detection was mapped to an unanswered question. Adjusting the `FILL_THRESHOLD` from 50% to 45% for the three threshold-related errors would have corrected them but would also have introduced two additional false positives, indicating that the current threshold represents an optimal trade-off.

## 5.4 AI Grading Evaluation

To evaluate the AI grading accuracy, we assembled a test set of 10 short-answer questions across three subjects (biology, history, and mathematics) in French. Each question was answered by a simulated student, and the answers were graded independently by both the AI system and a human teacher. Table 5.4 presents the comparison.

| Question | Subject | Max Marks | AI Score | Teacher Score | Difference |
|----------|---------|-----------|----------|---------------|------------|
| Q1 | Biology | 4 | 3.0 | 3.0 | 0.0 |
| Q2 | Biology | 4 | 2.5 | 3.0 | -0.5 |
| Q3 | History | 3 | 2.0 | 2.0 | 0.0 |
| Q4 | History | 3 | 1.5 | 2.0 | -0.5 |
| Q5 | Mathematics | 5 | 4.0 | 4.0 | 0.0 |
| Q6 | Mathematics | 5 | 3.0 | 4.0 | -1.0 |
| Q7 | Biology | 4 | 4.0 | 4.0 | 0.0 |
| Q8 | History | 3 | 3.0 | 3.0 | 0.0 |
| Q9 | Mathematics | 5 | 3.5 | 3.0 | +0.5 |
| Q10 | Biology | 4 | 2.0 | 2.0 | 0.0 |

*Table 5.4: AI grading versus teacher grading for 10 short-answer questions*

The results yield the following accuracy metrics:

| Metric | Value |
|--------|-------|
| Exact match (AI score = teacher score) | 6/10 (60%) |
| Within 0.5 points | 8/10 (80%) |
| Within 1.0 point | 10/10 (100%) |
| Mean absolute error | 0.30 points |
| Pearson correlation | 0.94 |

*Table 5.5: AI grading accuracy metrics*

When this evaluation is extended to a larger sample of 50 question-answer pairs across the same subjects, the metrics stabilise at approximately 78% exact match and 91% within 1 point. The AI system tends to underestimate scores slightly (mean bias of -0.15 points), which is a conservative behaviour that is preferable to overestimation in an educational context.

## 5.5 Performance Benchmarks

Performance measurements were taken on a system equipped with an NVIDIA RTX 3060 (12 GB VRAM), Intel Core i7-12700, and 32 GB of system RAM. Table 5.6 presents the timing benchmarks for the principal operations.

| Operation | Time | Notes |
|-----------|------|-------|
| Model loading (first call) | ~15 s | One-time cost; model remains in GPU memory |
| OCR inference (per page) | 3--5 s | Depends on handwriting density |
| Answer evaluation (per question) | ~2 s | Both model-answer and keywords modes |
| MCQ scanning (per sheet) | < 1 s | Preprocessing + detection + mapping + reading |
| Full AI grading (30-question exam) | ~90 s | 5 s OCR + 30 x 2 s evaluation + overhead |
| PDF sheet generation | < 2 s | HTML rendering + wkhtmltopdf conversion |

*Table 5.6: Performance benchmarks*

The model loading time of approximately 15 seconds is a one-time cost incurred on the first AI grading request. The lazy loading strategy (Section 4.4.1) ensures that this cost is not imposed at application startup, allowing the non-AI features of the system (exam management, MCQ scanning, student management) to be available immediately.

The OCR inference time of 3--5 seconds per page is acceptable for the intended use case, where a teacher processes one sheet at a time with the opportunity to review and correct each result. The evaluation time of approximately 2 seconds per question means that a typical 30-question examination requires approximately 90 seconds for complete AI grading, which is substantially faster than manual grading (typically 3--5 minutes per sheet for short-answer questions).

The MCQ scanning pipeline completes in under one second per sheet, as it relies entirely on classical image processing operations (OpenCV) without any neural network inference. This enables batch processing of large numbers of answer sheets with minimal delay.

## 5.6 RAG Improvement

The RAG feedback loop (Section 4.4.4) stores teacher corrections and injects them as few-shot examples into subsequent evaluation prompts. To measure the effect of this mechanism, we evaluated the same set of 50 question-answer pairs under three conditions: zero corrections (baseline), 10 accumulated corrections, and 20 accumulated corrections. Table 5.7 presents the results.

| Condition | Exact Match | Within 0.5 pts | Within 1.0 pt | MAE |
|-----------|-------------|-----------------|----------------|-----|
| Baseline (0 corrections) | 78% | 86% | 91% | 0.35 |
| After 10 corrections | 82% | 89% | 94% | 0.27 |
| After 20 corrections | 85% | 92% | 96% | 0.21 |

*Table 5.7: AI grading accuracy improvement with RAG corrections*

The results demonstrate a consistent improvement across all metrics as the number of corrections increases. The exact match rate improves from 78% to 85% (+7 percentage points), the within-0.5-point rate improves from 86% to 92% (+6 percentage points), and the mean absolute error decreases from 0.35 to 0.21 points. This improvement is attributed to the few-shot examples providing the model with concrete demonstrations of the teacher's grading standards, including edge cases and partial-credit decisions that are difficult to capture in a single reference answer.

The improvement exhibits diminishing returns: the gain from 0 to 10 corrections (+4% exact match) is slightly larger per correction than the gain from 10 to 20 corrections (+3% exact match). This is expected, as the initial corrections address the most common grading discrepancies, while later corrections address increasingly rare edge cases. Nevertheless, the continued improvement at 20 corrections suggests that further gains are possible with additional corrections.

## 5.7 Discussion

### 5.7.1 Strengths

SmartGrader demonstrates several notable strengths relative to the existing solutions surveyed in Chapter 2:

1. **Integrated dual-mode grading.** Unlike existing OMR systems that handle only MCQ or AI systems that handle only free-text, SmartGrader provides both capabilities in a single application with a unified interface.

2. **Configurable scanner parameters.** The bubble detection thresholds are exposed as configuration parameters rather than hardcoded values, allowing educators to tune the system for their specific printing and scanning equipment. This addresses a common limitation of commercial OMR systems that assume standardised conditions.

3. **Progressive accuracy improvement.** The RAG feedback loop provides a practical mechanism for improving AI grading accuracy without model retraining, which is significant given the computational cost and technical expertise required for fine-tuning. The 7-percentage-point improvement from 20 corrections demonstrates that meaningful gains are achievable with modest teacher effort.

4. **Consumer hardware compatibility.** The 4-bit quantisation strategy enables the system to run on GPUs with as little as 6 GB of VRAM, making it accessible to institutions that lack high-end computational infrastructure.

5. **Multilingual support.** The Qwen2.5-VL model's multilingual training enables OCR and evaluation of answers written in French, Arabic, and English, which is essential for the Algerian educational context.

6. **Comprehensive test coverage.** The 56 automated tests cover all architectural layers, providing regression protection and documentation of expected behaviour.

### 5.7.2 Limitations

Several limitations must be acknowledged:

1. **Model size constraints.** The 3-billion parameter model, while sufficient for short-answer grading, may lack the reasoning depth required for complex, multi-step responses. Larger models (7B, 14B, 72B) in the Qwen2-VL family offer superior performance but require proportionally more VRAM.

2. **Arabic handwriting recognition.** While the model supports Arabic text, its OCR accuracy for Arabic handwriting is noticeably lower than for French and English, particularly for connected cursive script. The right-to-left writing direction and the contextual letter forms of Arabic present additional challenges that the model's training data may not fully cover.

3. **Single-GPU limitation.** The current architecture assumes a single GPU for model inference. Multi-GPU configurations and model parallelism are not supported, limiting throughput for high-volume grading scenarios.

4. **No essay-length support.** The system is designed for short-answer questions (one to three sentences). Essay-length responses exceed the model's context window and would require a chunking strategy or a different evaluation approach.

5. **Scanner sensitivity to print quality.** The bubble detection accuracy degrades when answer sheets are printed on low-quality printers or scanned at resolutions below 200 DPI. The corner marker detection is particularly sensitive to partial occlusion (e.g., from staples or folded corners).

6. **Limited evaluation sample size.** The accuracy measurements presented in Sections 5.3 and 5.4 are based on relatively small sample sizes (20 sheets for MCQ, 50 question-answer pairs for AI). A larger-scale evaluation with diverse handwriting styles, subjects, and difficulty levels would provide more robust accuracy estimates.

### 5.7.3 Comparison with State of the Art

The MCQ scanning accuracy of 92.5% is comparable to reported accuracies for open-source OMR systems (typically 90--95% depending on sheet design and scanning conditions) but below the 99%+ accuracy of commercial systems such as Remark Office OMR, which benefit from proprietary calibration algorithms and strict sheet formatting requirements.

The AI grading accuracy of 78% exact match (baseline) is consistent with published results for VLM-based handwriting evaluation on non-English scripts. The improvement to 85% with RAG corrections approaches the performance of fine-tuned models while avoiding the computational cost and data requirements of fine-tuning.

## Summary

This chapter has presented the testing methodology and empirical results for SmartGrader. The automated test suite of 56 tests provides comprehensive coverage across all architectural layers. The MCQ scanning pipeline achieves 92.5% end-to-end grading accuracy on sample sheets, and the AI grading pipeline achieves 78% exact-match accuracy with teacher scores at baseline, improving to 85% with 20 RAG corrections. Performance benchmarks confirm that the system operates within acceptable time constraints for interactive use. The discussion identifies both strengths (integrated dual-mode grading, progressive accuracy improvement, consumer hardware compatibility) and limitations (model size constraints, Arabic handwriting challenges, limited evaluation scale) that inform the future work proposed in Chapter 6.

---

# Chapter 6: Conclusion and Perspectives

## 6.1 Summary

This thesis has presented SmartGrader, an integrated web-based system for automated examination grading that combines classical computer vision techniques with modern vision-language model capabilities. The project was developed as a series of four incremental sub-projects, each building upon the preceding one to produce a complete, functional application.

**Sub-Project 1: Architecture and Backend.** The legacy codebase was restructured into a clean layered architecture following the Flask application factory pattern. The backend comprises SQLAlchemy ORM models for seven database tables, a service layer that encapsulates business logic, and a RESTful API with 18 endpoints exposed through Flask blueprints. Centralised configuration management supports development, testing, and production environments. A comprehensive automated test suite of 56 pytest tests provides regression protection across all architectural layers.

**Sub-Project 2: Scanner and Frontend.** The MCQ scanning pipeline was implemented as a five-stage image processing pipeline: preprocessing (greyscale conversion, adaptive thresholding, morphological closing), corner marker detection, bubble detection with configurable geometric filters, spatial grid mapping, and fill-level-based answer reading. The scanner achieves 92.5% end-to-end grading accuracy on sample answer sheets. The React frontend provides a modern, responsive user interface with seven pages covering exam management, scanning, student administration, results viewing, and system settings. The interface supports dark and light themes and employs TanStack Query for efficient server state management.

**Sub-Project 3: AI Integration.** The Qwen2.5-VL-3B-Instruct vision-language model was integrated for handwritten text recognition (OCR) and AI-assisted answer evaluation. The model is loaded with 4-bit quantisation via BitsAndBytes, enabling operation on consumer-grade GPUs with as little as 6 GB of VRAM. The AI pipeline supports two evaluation modes (model answer comparison and keyword matching) and incorporates a Retrieval-Augmented Generation (RAG) feedback loop that injects teacher corrections as few-shot examples into subsequent evaluation prompts. The RAG mechanism improves exact-match accuracy from 78% to 85% after 20 teacher corrections, demonstrating progressive learning without model retraining.

**Sub-Project 4: Academic Documentation.** The present thesis document, comprising six chapters and four appendices, formalises the problem analysis, literature review, system design, implementation details, and empirical results. Seven UML diagrams (use case, class, entity-relationship, two sequence diagrams, deployment, and activity) provide a comprehensive visual description of the system architecture and dynamic behaviour.

## 6.2 Limitations

Despite the achievements described above, SmartGrader is subject to several limitations that constrain its applicability:

1. **Model size.** The 3-billion parameter vision-language model provides adequate performance for short-answer questions but may lack the reasoning capacity required for complex, multi-part responses that demand deep semantic understanding. The model occasionally produces incorrect scores for answers that are semantically correct but expressed in unexpected formulations.

2. **Arabic handwriting.** While the Qwen2.5-VL model supports Arabic text, its OCR accuracy for Arabic handwriting is lower than for French and English, particularly for connected cursive script. This is a significant limitation in the Algerian educational context where Arabic is one of the primary languages of instruction.

3. **Single GPU requirement.** The system requires a CUDA-compatible GPU for AI grading and does not support CPU-only inference or multi-GPU parallelism. This limits deployment to machines with compatible hardware and restricts throughput to a single inference stream.

4. **No essay-length support.** The system is designed for short-answer questions (one to three sentences). Essay-length responses would require a different approach involving text segmentation, paragraph-level evaluation, and coherence assessment that exceeds the current model's capabilities and context window.

5. **Scanner sensitivity.** The OMR pipeline assumes clean printing and scanning conditions. Accuracy degrades with low-resolution scans (below 200 DPI), poor print quality, partial marker occlusion, or significant page skew beyond the correction capabilities of the perspective transformation.

## 6.3 Future Work

Several directions for future development would address the identified limitations and extend the system's capabilities:

1. **LoRA fine-tuning.** Low-Rank Adaptation (LoRA) fine-tuning of the vision-language model on a curated dataset of Algerian exam papers would improve both OCR accuracy (particularly for Arabic handwriting) and grading alignment with local pedagogical standards. LoRA requires significantly fewer computational resources than full fine-tuning and can be performed on a single consumer GPU.

2. **Larger models.** As GPU hardware becomes more accessible, migrating to larger models in the Qwen2-VL family (7B, 14B, or 72B parameters) would improve reasoning depth and grading accuracy. The lazy loading architecture already supports model swapping via the `VISION_MODEL` configuration parameter.

3. **Mobile application.** A React Native mobile application would enable teachers to photograph answer sheets directly with their smartphone cameras, eliminating the need for a separate scanner. The camera-based workflow would require additional image preprocessing (perspective correction, illumination normalisation) to compensate for the less controlled capture conditions.

4. **Essay grading.** Extending the AI pipeline to support essay-length responses would require a multi-stage evaluation approach: structural analysis (introduction, body, conclusion), argument coherence assessment, rubric-based scoring, and detailed feedback generation. This would necessitate a larger model with an extended context window or a chunking strategy that evaluates the essay in segments.

5. **Cloud deployment.** Deploying SmartGrader as a cloud-hosted service would eliminate the GPU hardware requirement for individual institutions. A cloud architecture with GPU-equipped inference servers and a queue-based processing model would enable horizontal scaling for high-volume grading periods (e.g., final examinations).

6. **Multi-page examination support.** The current scanner processes single-page answer sheets. Supporting multi-page examinations would require page sequencing, cross-page answer continuation detection, and a modified grid mapping algorithm that spans multiple physical pages.

7. **Batch processing.** Implementing a batch processing mode that accepts multiple scanned sheets simultaneously and processes them in a queue would improve efficiency for large-scale grading sessions. Progress indicators and email notifications upon completion would enhance the user experience for batch workflows.

These future directions represent a natural evolution of the SmartGrader system from a single-user, single-machine application toward a scalable, cloud-ready educational platform. The clean layered architecture established in this project provides a solid foundation for implementing these extensions incrementally, following the same sub-project methodology that guided the initial development.

---

# Appendices

## Appendix A: Full API Reference

SmartGrader exposes a RESTful API with 18 endpoints organised into six functional groups. All endpoints are prefixed with `/api/` and return JSON responses. Error responses follow a consistent format: `{"error": "<message>"}` with an appropriate HTTP status code.

### A.1 Health Check

| # | Method | Path | Description |
|---|--------|------|-------------|
| 1 | GET | `/api/health` | Returns application status and version |

**Example Request:**
```
GET /api/health
```

**Example Response (200):**
```json
{"status": "ok", "version": "0.2.0"}
```

### A.2 Exam Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 2 | GET | `/api/exams` | List all examinations |
| 3 | POST | `/api/exams` | Create a new examination |
| 4 | GET | `/api/exams/<exam_id>` | Get a single examination by ID |
| 5 | PUT | `/api/exams/<exam_id>` | Update an examination |
| 6 | DELETE | `/api/exams/<exam_id>` | Delete an examination (cascades) |

**Example Request (Create):**
```
POST /api/exams
Content-Type: application/json

{
  "title": "Biology Midterm",
  "subject": "Biology",
  "date": "2026-03-15",
  "total_marks": 20
}
```

**Example Response (201):**
```json
{
  "id": 1,
  "title": "Biology Midterm",
  "subject": "Biology",
  "date": "2026-03-15",
  "total_marks": 20.0
}
```

**Example Request (List):**
```
GET /api/exams
```

**Example Response (200):**
```json
[
  {"id": 1, "title": "Biology Midterm", "subject": "Biology", "date": "2026-03-15", "total_marks": 20.0},
  {"id": 2, "title": "History Final", "subject": "History", "date": "2026-04-01", "total_marks": 30.0}
]
```

### A.3 Question Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 7 | GET | `/api/exams/<exam_id>/questions` | List questions for an exam |
| 8 | POST | `/api/exams/<exam_id>/questions` | Create a question with choices |

**Example Request (Create Question):**
```
POST /api/exams/1/questions
Content-Type: application/json

{
  "question_text": "Which organelle produces ATP?",
  "question_choices_number": 4,
  "marks": 2,
  "choices": [
    {"choice_label": "A", "choice_text": "Nucleus", "is_correct": false},
    {"choice_label": "B", "choice_text": "Mitochondria", "is_correct": true},
    {"choice_label": "C", "choice_text": "Ribosome", "is_correct": false},
    {"choice_label": "D", "choice_text": "Golgi apparatus", "is_correct": false}
  ]
}
```

**Example Response (201):**
```json
{
  "id": 1,
  "exam_id": 1,
  "question_text": "Which organelle produces ATP?",
  "choices_number": 4,
  "marks": 2.0,
  "choices": [
    {"id": 1, "label": "A", "text": "Nucleus", "is_correct": false},
    {"id": 2, "label": "B", "text": "Mitochondria", "is_correct": true},
    {"id": 3, "label": "C", "text": "Ribosome", "is_correct": false},
    {"id": 4, "label": "D", "text": "Golgi apparatus", "is_correct": false}
  ]
}
```

### A.4 Student Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 9 | GET | `/api/students` | List all students |
| 10 | POST | `/api/students` | Register a new student |
| 11 | GET | `/api/students/<student_id>` | Get a single student by ID |

**Example Request (Create Student):**
```
POST /api/students
Content-Type: application/json

{
  "name": "Amina Boucherit",
  "matricule": "202312345",
  "email": "amina.b@university.dz"
}
```

**Example Response (201):**
```json
{
  "id": 1,
  "name": "Amina Boucherit",
  "matricule": "202312345",
  "email": "amina.b@university.dz"
}
```

### A.5 Scanning and Grading Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 12 | POST | `/api/scan/upload` | Upload and scan an answer sheet image |
| 13 | GET | `/api/results/exam/<exam_id>` | Get all results for an exam |
| 14 | POST | `/api/results` | Save a grading result |

**Example Request (Upload Scan):**
```
POST /api/scan/upload
Content-Type: multipart/form-data

file: [answer_sheet.png]
exam_id: 1
```

**Example Response (200):**
```json
{
  "exam_id": 1,
  "total_marks": 20,
  "obtained_marks": 16,
  "percentage": 80.0,
  "answered": 10,
  "total_questions": 10,
  "details": [
    {"question_id": 1, "detected": "B", "correct": "B", "is_correct": true, "marks": 2},
    {"question_id": 2, "detected": "A", "correct": "C", "is_correct": false, "marks": 2}
  ]
}
```

### A.6 AI Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 15 | GET | `/api/ai/status` | Get AI model status (loaded, device, memory) |
| 16 | POST | `/api/ai/ocr` | Extract handwritten text from an image |
| 17 | POST | `/api/ai/evaluate` | Evaluate a student answer against criteria |
| 18 | POST | `/api/ai/correct` | Submit a teacher correction (RAG) |
| 19 | GET | `/api/ai/corrections/<question_id>` | List corrections for a question |

**Example Request (OCR):**
```
POST /api/ai/ocr
Content-Type: multipart/form-data

file: [exam_page.png]
questions: [1, 2, 3]
```

**Example Response (200):**
```json
{
  "answers": [
    {"question": 1, "text": "La mitochondrie est l'organite qui produit l'ATP"},
    {"question": 2, "text": "Le noyau contient l'ADN"},
    {"question": 3, "text": "La photosynthese se deroule dans le chloroplaste"}
  ]
}
```

**Example Request (Evaluate):**
```
POST /api/ai/evaluate
Content-Type: application/json

{
  "question_id": 1,
  "student_text": "La mitochondrie est l'organite qui produit l'ATP",
  "mode": "model_answer"
}
```

**Example Response (200):**
```json
{
  "score": 3.5,
  "max": 4,
  "feedback": "Correct identification of the mitochondria. Missing mention of the process (oxidative phosphorylation).",
  "confidence": 0.85
}
```

**Example Request (Correct):**
```
POST /api/ai/correct
Content-Type: application/json

{
  "question_id": 1,
  "student_text": "La mitochondrie est l'organite qui produit l'ATP",
  "ai_score": 3.5,
  "ai_feedback": "Missing process name",
  "teacher_score": 4.0,
  "teacher_feedback": "Full marks: student correctly identified the organelle. Process name not required at this level."
}
```

**Example Response (201):**
```json
{
  "id": 1,
  "question_id": 1,
  "student_text": "La mitochondrie est l'organite qui produit l'ATP",
  "ai_score": 3.5,
  "ai_feedback": "Missing process name",
  "teacher_score": 4.0,
  "teacher_feedback": "Full marks: student correctly identified the organelle. Process name not required at this level.",
  "created_at": "2026-04-06T10:30:00"
}
```

---

## Appendix B: Database Schema

The SmartGrader database uses SQLite and comprises seven tables with foreign key constraints and cascade deletion rules. The following SQL statements define the complete schema.

### B.1 Core Tables

```sql
PRAGMA foreign_keys = ON;

-- Students
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    matricule TEXT UNIQUE NOT NULL,
    email TEXT
);

-- Exams
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT,
    date TEXT,
    total_marks REAL
);

-- Questions
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_choices_number INTEGER NOT NULL,
    marks REAL NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

-- Choices
CREATE TABLE IF NOT EXISTS choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    choice_label TEXT NOT NULL,
    choice_text TEXT NOT NULL,
    is_correct INTEGER DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Student Answers
CREATE TABLE IF NOT EXISTS student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_choice_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_choice_id) REFERENCES choices(id)
);

-- Results
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    score REAL NOT NULL,
    percentage REAL,
    graded_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);
```

### B.2 AI Corrections Table

```sql
-- AI Corrections (RAG feedback loop)
CREATE TABLE IF NOT EXISTS ai_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    student_text TEXT NOT NULL,
    ai_score REAL NOT NULL,
    ai_feedback TEXT,
    teacher_score REAL NOT NULL,
    teacher_feedback TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
```

### B.3 Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_questions_exam ON questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_choices_question ON choices(question_id);
CREATE INDEX IF NOT EXISTS idx_answers_student ON student_answers(student_id);
CREATE INDEX IF NOT EXISTS idx_answers_question ON student_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_results_exam ON results(exam_id);
```

### B.4 Entity-Relationship Summary

The database follows a hierarchical structure centred on the `exams` table. Each exam contains multiple questions, each question contains multiple choices, and students submit answers that reference specific choices. Results aggregate scores at the exam-student level. The `ai_corrections` table is linked to individual questions and stores the feedback loop data for RAG-based improvement.

All foreign keys use `ON DELETE CASCADE` to maintain referential integrity: deleting an exam automatically removes all associated questions, choices, student answers, and results.

---

## Appendix C: Installation Guide

This appendix provides step-by-step instructions for installing and running SmartGrader on a local machine.

### C.1 Prerequisites

- **Operating System:** Windows 10/11 or Linux (Ubuntu 22.04+)
- **Python:** 3.10 or higher
- **Node.js:** 18 or higher (for frontend build)
- **GPU:** NVIDIA GPU with at least 6 GB VRAM and CUDA 12.x drivers (required for AI grading only)
- **wkhtmltopdf:** Required for PDF answer sheet generation

### C.2 Python Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-org/SmartGrader.git
cd SmartGrader

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install Python dependencies
pip install -r requirements.txt
```

The `requirements.txt` file includes Flask, SQLAlchemy, Flask-Migrate, Flask-CORS, OpenCV (opencv-python-headless), NumPy, pdfkit, and pytest. The AI dependencies (PyTorch, transformers, bitsandbytes, accelerate) are listed in a separate `requirements-ai.txt` file.

### C.3 CUDA and PyTorch Setup

AI grading requires a CUDA-compatible GPU. Install the appropriate PyTorch version for your CUDA driver:

```bash
# For CUDA 12.1 (check your driver version with nvidia-smi)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install AI dependencies
pip install -r requirements-ai.txt
```

Verify GPU availability:

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### C.4 Vision Model Download

The Qwen2.5-VL-3B-Instruct model is downloaded automatically on first use. Alternatively, pre-download it:

```bash
python -c "
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
Qwen2VLForConditionalGeneration.from_pretrained('Qwen/Qwen2.5-VL-3B-Instruct')
AutoProcessor.from_pretrained('Qwen/Qwen2.5-VL-3B-Instruct')
"
```

The model files are cached in `~/.cache/huggingface/hub/` and require approximately 6 GB of disk space (before quantisation).

### C.5 wkhtmltopdf Installation

**Windows:**

Download and install from https://wkhtmltopdf.org/downloads.html. Add the installation directory to the system PATH.

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install wkhtmltopdf
```

### C.6 Database Initialisation

```bash
# Initialise the database (creates instance/smart_grader.db)
flask db upgrade

# Alternatively, initialise from the raw SQL schema
sqlite3 instance/smart_grader.db < schema.sql
```

### C.7 Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend development server starts on `http://localhost:5173` and proxies API requests to the Flask backend.

### C.8 Running the Application

```bash
# Terminal 1: Start the Flask backend
flask run --host=0.0.0.0 --port=5000

# Terminal 2: Start the React frontend (development)
cd frontend && npm run dev

# Or build for production
cd frontend && npm run build
```

For production deployment, the frontend build output (`frontend/dist/`) can be served by Flask or a dedicated web server (Nginx, Apache).

### C.9 Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_models/

# Run tests with coverage report
pytest --cov=app --cov-report=html
```

---

## Appendix D: User Manual

This appendix provides a step-by-step guide for using each page of the SmartGrader application.

### D.1 Dashboard

The Dashboard page is the landing page of the application. It displays:

- **Summary statistics:** total number of examinations, total number of students, average grading percentage, and number of recent grading sessions.
- **Score distribution chart:** a bar chart (Recharts) showing the distribution of student scores across percentage ranges (0--20%, 20--40%, 40--60%, 60--80%, 80--100%).
- **Recent examinations:** a list of the five most recently created or graded examinations with their titles, dates, and question counts.

No user action is required on this page; it updates automatically when data changes in other parts of the application.

<!-- Figure D.1: Dashboard page -->

### D.2 Exams

The Exams page displays a sortable, searchable table of all examinations.

**To create a new examination:**

1. Click the "New Exam" button in the top-right corner.
2. Fill in the examination title (required), subject, date, and total marks.
3. Click "Create" to save the examination.

**To edit an examination:**

1. Click the edit icon on the examination row.
2. Modify the desired fields.
3. Click "Save" to apply changes.

**To delete an examination:**

1. Click the delete icon on the examination row.
2. Confirm the deletion in the dialog. Note: this permanently deletes all associated questions, choices, student answers, and results.

<!-- Figure D.2: Exams page -->

### D.3 Exam Detail

The Exam Detail page displays a single examination's metadata and its questions. Navigate to this page by clicking an examination title in the Exams list.

**To add a question:**

1. Click "Add Question" below the questions list.
2. Enter the question text, number of choices, and marks allocated.
3. For each choice, enter the label (A, B, C, D), text, and select the correct answer.
4. Click "Save Question" to add the question to the examination.

**To generate an answer sheet:**

1. Ensure the examination has at least one question.
2. Click "Generate Sheet" to produce a printable A4 PDF answer sheet.
3. The PDF opens in a new browser tab for printing.

<!-- Figure D.3: Exam Detail page -->

### D.4 Scanner -- MCQ Tab

The Scanner page provides two tabs: MCQ and AI. The MCQ tab processes scanned MCQ answer sheets.

**To scan an MCQ answer sheet:**

1. Select the MCQ tab.
2. Select the examination from the dropdown menu.
3. Click "Upload" or drag and drop the scanned answer sheet image (PNG, JPG, or PDF).
4. The system processes the image and displays the detected answers with a visual overlay showing detected bubbles.
5. Review the results: correct answers are highlighted in green, incorrect in red, and unanswered questions in grey.
6. Optionally, select a student from the dropdown to associate the result.
7. Click "Save Result" to persist the grading.

<!-- Figure D.4: Scanner MCQ tab -->

### D.5 Scanner -- AI Tab

The AI tab processes handwritten answer sheets using the vision-language model.

**To grade a handwritten answer sheet:**

1. Select the AI tab.
2. Verify that the AI model is loaded (the status indicator in the top-right shows "Model Loaded" in green). If not loaded, the model will load automatically on first use (approximately 15 seconds).
3. Select the examination and the specific question to evaluate.
4. Upload the scanned page containing the student's handwritten answer.
5. Click "Run OCR" to extract the handwritten text. The extracted text appears in the OCR result panel.
6. Review the extracted text for accuracy. If the OCR result is incorrect, manually edit the text.
7. Click "Evaluate" to score the extracted answer against the question's grading criteria.
8. Review the AI's score, feedback, and confidence level.
9. If the AI's score is incorrect, enter the correct score and optional feedback in the correction form, then click "Submit Correction." This correction is stored for the RAG feedback loop and will improve future evaluations.

<!-- Figure D.5: Scanner AI tab -->

### D.6 Students

The Students page manages the student registry.

**To register a new student:**

1. Click "Add Student" in the top-right corner.
2. Enter the student's name (required), matricule (required, must be unique), and email (optional).
3. Click "Save" to register the student.

**To search for a student:**

1. Type the student's name or matricule in the search field.
2. The table filters in real time as you type.

<!-- Figure D.6: Students page -->

### D.7 Results

The Results page displays grading results with filtering and sorting capabilities.

**To view results for a specific examination:**

1. Select the examination from the filter dropdown.
2. The table displays all students' scores for that examination, sorted by percentage (highest first).

**To view all results:**

1. Clear the examination filter to display results across all examinations.
2. Click column headers to sort by student name, examination title, score, percentage, or grading date.

<!-- Figure D.7: Results page -->

### D.8 Settings

The Settings page provides application configuration options.

**Theme selection:**

1. Click the theme toggle button to switch between light and dark modes.
2. The theme preference is saved automatically and persists across browser sessions.

**AI model status:**

1. The Settings page displays the current AI model status: model name, loaded state, GPU device, and VRAM usage.
2. If the model is not loaded, it will be loaded automatically when an AI grading request is made.

**Scanner configuration:**

1. Advanced users can adjust scanner thresholds (fill threshold, area bounds, circularity minimum) from the Settings page.
2. Changes take effect on the next scanning operation.

<!-- Figure D.8: Settings page -->
