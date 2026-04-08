# Chapter 2: State of the Art

This chapter surveys the existing literature, technologies, and commercial solutions relevant to the automated grading and online administration of examinations. We begin by reviewing established Optical Mark Recognition systems, then examine online examination platforms and their limitations. We proceed to discuss online proctoring solutions, browser-based face detection frameworks, and the JWT authentication standard. We then survey the computer vision techniques that underpin document analysis, review the emerging family of Vision Language Models and their application to handwriting recognition, and introduce Retrieval-Augmented Generation as a mechanism for improving model accuracy. The chapter concludes with an expanded comparative synthesis and an identification of the gaps that motivate the SmartGrader project.

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

## 2.2 Online Examination Platforms

Online examination platforms deliver assessments through web browsers, eliminating the need for physical answer sheets. This section reviews the principal platforms in this category and their respective limitations.

### 2.2.1 Moodle Quiz (Online Mode)

Beyond its use with paper-based assessments, Moodle's Quiz module is widely deployed for online examinations in university settings. It supports a broad range of question types (multiple-choice, true/false, short answer, essay, matching, numerical) and provides configurable timing, shuffled questions, and multiple attempts. Moodle is open-source, making it free for institutions to deploy, and its plugin ecosystem provides extensions for additional question types and integrations. Its principal limitations in the online examination context are its monolithic architecture, which demands significant server resources, and its dependence on a separate LMS installation rather than operating as a standalone examination tool. Moodle's native anti-cheat capabilities are also limited, relying primarily on question shuffling and time limits rather than active proctoring.

### 2.2.2 Google Forms

Google Forms provides a free, cloud-hosted survey and quiz tool that is widely used for informal online assessments. Its simplicity and zero-configuration deployment make it attractive for small classes, but it lacks the academic rigour required for formal examinations: there is no identity verification, no session control, no time-per-question enforcement, and no proctoring mechanism of any kind. Results are stored in Google Sheets, and integration with institutional student information systems is absent.

### 2.2.3 ExamSoft (Examplify)

ExamSoft is a dedicated secure examination platform widely used in professional education (law schools, medical schools) and higher education. The Examplify desktop client locks down the student's computer during the examination, disabling access to the internet, local files, and other applications. ExamSoft supports rich question types including audio and video stimuli and provides detailed analytics. However, ExamSoft is a proprietary, subscription-based platform with per-seat or per-exam pricing that places it out of reach for publicly funded Algerian institutions. Its lockdown client requires installation on the student's personal computer and does not support browser-based delivery.

### 2.2.4 Comparison of Online Examination Platforms

| Criterion | Moodle Quiz | Google Forms | ExamSoft | **SmartGrader** |
|-----------|-------------|-------------|----------|----------------|
| MCQ support | Yes | Yes | Yes | **Yes** |
| Timed sessions | Yes | No | Yes | **Yes** |
| Auto-submit on timeout | Yes | No | Yes | **Yes** |
| Student groups | Yes | No | Yes | **Yes** |
| Role-based access | Yes | No | Yes | **Yes** |
| Open source | Yes | No | No | **Yes** |
| Paper scanning | No | No | No | **Yes** |
| AI grading | No | No | No | **Yes** |
| Browser-based proctoring | No | No | No | **Yes** |
| Self-hosted | Yes | No | No | **Yes** |
| Pricing | Free | Free | Subscription | **Free** |

## 2.3 Online Proctoring Solutions

Academic integrity in online examinations is enforced through proctoring technologies that monitor student behaviour during the examination session. This section surveys the principal approaches.

### 2.3.1 ProctorU

ProctorU is a human-assisted remote proctoring service in which a live proctor observes the student via webcam and screen share throughout the examination. The proctor can communicate with the student through a chat interface and can flag suspicious behaviour. While ProctorU provides a high level of monitoring confidence, it is expensive (charged per examination session), requires scheduling in advance, and raises privacy concerns due to the transmission of live video to a third-party service. It also requires a stable, high-bandwidth internet connection that may not be available to all Algerian students.

### 2.3.2 Respondus LockDown Browser

Respondus LockDown Browser is a custom browser that prevents students from navigating to other websites, opening other applications, or capturing screenshots during an examination. It integrates with Moodle, Canvas, and Blackboard. The companion Respondus Monitor product adds webcam recording and automated behavioural analysis. LockDown Browser requires installation on the student's machine and is not available as a browser extension or progressive web app, limiting its deployment flexibility. The recorded video is uploaded to Respondus servers for post-hoc review, raising data sovereignty concerns.

### 2.3.3 Proctorio

Proctorio is a browser extension-based proctoring solution that intercepts webcam, microphone, and screen data during an examination and applies automated analysis algorithms to detect suspicious behaviour. It integrates with major LMS platforms and provides risk scores based on gaze direction, audio activity, and window focus changes. Proctorio has been controversial due to privacy concerns: it records students' faces and environments, stores data on cloud servers, and has been the subject of academic freedom debates. Its automated risk scores have also been criticised for false positives, particularly for students with disabilities or those taking examinations in non-standard environments.

### 2.3.4 Comparative Analysis of Proctoring Solutions

| Criterion | ProctorU | Respondus Monitor | Proctorio | **SmartGrader** |
|-----------|----------|------------------|-----------|----------------|
| Live human proctor | Yes | No | No | **No** |
| Webcam monitoring | Yes | Yes | Yes | **Yes (snapshots)** |
| Browser lockdown | No | Yes | Partial | **Yes (fullscreen)** |
| Tab-switch detection | No | No | Yes | **Yes** |
| Face detection | Human | Automated | Automated | **TF.js BlazeFace** |
| Server-side video | Yes | Yes | Yes | **No (snapshots only)** |
| Privacy-preserving | No | No | No | **Yes (local)** |
| Open source | No | No | No | **Yes** |
| Requires installation | No | Yes | Extension | **No** |
| Cost | Per session | Subscription | Subscription | **Free** |

A key distinguishing feature of SmartGrader's approach is that it performs all face detection locally in the browser using TensorFlow.js, transmitting only discrete snapshots rather than continuous video streams. This significantly reduces privacy exposure and bandwidth requirements compared to server-side proctoring systems.

## 2.4 Browser-Based Face Detection

The feasibility of running real-time face detection directly within a web browser, without any server-side computation, has been established by the emergence of WebGL-accelerated machine learning frameworks.

### 2.4.1 TensorFlow.js

TensorFlow.js [@tensorflowjs2024] is a JavaScript library that enables the training and deployment of machine learning models entirely within the browser using WebGL for GPU acceleration. It provides a high-level API for model inference, supports the conversion of TensorFlow SavedModels and Keras models to the TensorFlow.js format, and offers a set of pre-trained models through the `@tensorflow-models` package family. TensorFlow.js achieves inference latencies of tens to hundreds of milliseconds for compact models on modern hardware, making real-time face detection feasible at examination-relevant frequencies (one check per second or faster).

### 2.4.2 MediaPipe

MediaPipe [@mediapipe2024], developed by Google, is a cross-platform framework for applying ML pipelines to media streams. Its FaceMesh and Face Detection solutions provide real-time face tracking in the browser via a WebAssembly backend. MediaPipe face detection offers sub-10-millisecond latency for a single face on modern hardware and provides rich facial landmark data including eye gaze estimation and head pose. Its primary limitation is the larger package size compared to BlazeFace, which increases initial page load time.

### 2.4.3 BlazeFace

BlazeFace [@blazeface2019] is a lightweight face detection model originally developed by Google for mobile devices. It detects faces using a single-shot approach with anchor-based regression, achieving real-time performance on mobile CPUs (less than 2 ms per frame). In TensorFlow.js, BlazeFace is available through the `@tensorflow-models/blazeface` package and requires approximately 300 KB of model weights. It is optimised for front-facing, near-field scenarios such as a student looking at a laptop webcam — exactly the use case required for examination proctoring. SmartGrader employs BlazeFace through TensorFlow.js for its low weight, fast inference, and suitability for the examination monitoring context.

### 2.4.4 Comparison of Browser-Based Face Detection Options

| Model | Package Size | Inference Latency | Face Landmarks | Gaze Estimation | Suitable for Exam Proctoring |
|-------|-------------|-------------------|----------------|-----------------|------------------------------|
| BlazeFace (TF.js) | ~300 KB | < 2 ms | Minimal | No | Yes |
| MediaPipe Face Detection | ~2 MB | < 10 ms | Yes | No | Yes |
| MediaPipe FaceMesh | ~4 MB | ~5 ms | 468 points | Estimated | Yes (advanced) |
| face-api.js | ~6 MB | ~10-30 ms | 68 points | No | Yes |

SmartGrader selects BlazeFace for its minimal footprint and fast inference, which allows face presence checks to run at 1-second intervals without perceptible impact on examination performance.

## 2.5 JWT Authentication in Web Applications

Authentication is a foundational requirement for any multi-user web application. This section reviews the JWT standard and its applicability to the SmartGrader context.

### 2.5.1 JSON Web Tokens

JSON Web Tokens (JWT), standardised in RFC 7519 [@rfc7519], are a compact, URL-safe means of representing claims between two parties. A JWT consists of three Base64URL-encoded components separated by dots: a header specifying the algorithm (typically HMAC-SHA256 or RS256), a payload containing the claims (issuer, subject, expiration time, and custom claims such as role), and a cryptographic signature that allows the recipient to verify the token's integrity without querying a database.

The stateless nature of JWT is particularly valuable for REST APIs: the server signs the token at login time and need not maintain server-side session state. Each subsequent request carries the token in the `Authorization` header, and the server validates the signature and claims locally. This enables horizontal scaling (any server instance can validate any token) and simplifies deployment.

### 2.5.2 JWT in Educational Platforms

Several major educational platforms employ JWT for API authentication. Canvas LMS uses OAuth 2.0 bearer tokens (which are JWTs) for its REST API. Moodle's Web Services API supports token-based authentication as an alternative to session cookies. The use of JWT in SmartGrader aligns with industry practice and enables the React frontend to authenticate against the Flask backend without shared session state, facilitating the separation of concerns between the two application tiers.

### 2.5.3 Role-Based Access Control

SmartGrader implements a two-role access control model: Teacher and Student. The JWT payload encodes the authenticated user's role, and Flask route decorators inspect this claim to enforce access control at the endpoint level. This approach ensures that student-facing endpoints (exam retrieval, answer submission) are inaccessible to unauthenticated users, while teacher-facing endpoints (exam creation, result viewing, proctoring dashboard) are restricted to accounts with the Teacher role.

## 2.6 Computer Vision for Document Analysis

The processing of scanned examination sheets requires a suite of computer vision techniques to identify structural elements (markers, grids, bubbles) and to extract meaningful information from the document image. This section reviews the principal techniques employed in the SmartGrader scanner pipeline.

### 2.6.1 The Hough Transform

The Hough Transform, originally proposed by Hough [@hough1962method] for detecting lines in bubble chamber photographs, was subsequently generalised by Ballard [@ballard1981generalizing] to detect arbitrary shapes including circles and ellipses. In the context of OMR, the Circular Hough Transform is a fundamental technique for detecting filled bubbles on answer sheets. The algorithm maps each edge pixel in the image to a three-dimensional parameter space (centre x, centre y, radius), and accumulator cells that exceed a threshold indicate the presence of circles at the corresponding locations.

The OpenCV library [@opencv2024] provides an efficient implementation of the Circular Hough Transform through the `HoughCircles` function, which combines edge detection via the Canny algorithm with the accumulator-based circle detection. SmartGrader employs this function with carefully tuned parameters (minimum radius of 6 pixels, maximum radius of 25 pixels, circularity threshold of 0.65) to detect answer bubbles while filtering out noise and spurious detections.

### 2.6.2 Contour Detection

Contour detection is the process of identifying the boundaries of objects within an image. In OpenCV, the `findContours` function traces the outlines of connected white regions in a binary image, returning a hierarchical list of contour polygons. SmartGrader uses contour detection for two purposes: first, to locate the four corner markers (large filled squares) that define the coordinate system of the answer sheet; and second, to identify individual answer bubbles as an alternative to the Hough Transform when bubble shapes deviate from perfect circles.

Contour-based detection offers greater flexibility than the Hough Transform in accommodating printing imperfections and scan distortions. By computing contour properties such as area, aspect ratio, and circularity (the ratio of the contour area to the area of its minimum enclosing circle), the system can robustly discriminate between answer bubbles and other structural elements of the sheet.

### 2.6.3 Morphological Operations

Mathematical morphology provides a set of operations for processing binary and greyscale images based on the interaction of the image with a structuring element. The two fundamental operations are erosion (which shrinks bright regions) and dilation (which expands them). Their combination yields opening (erosion followed by dilation, which removes small bright spots) and closing (dilation followed by erosion, which fills small dark gaps).

In the SmartGrader scanner pipeline, morphological operations serve as a preprocessing step to clean the binarised image before bubble detection. Opening is applied to remove scanning noise such as dust and paper texture artefacts, while closing ensures that incompletely filled bubbles are treated as solid marks. These operations significantly improve detection reliability, particularly when processing sheets that have been scanned at lower resolutions or with consumer-grade equipment.

### 2.6.4 Adaptive Thresholding

Thresholding is the process of converting a greyscale image to a binary image by classifying each pixel as either foreground or background based on its intensity value. Global thresholding applies a single threshold to the entire image, which performs poorly when illumination varies across the document surface -- a common occurrence with flatbed scanners that exhibit uneven lighting.

Adaptive thresholding addresses this limitation by computing a local threshold for each pixel based on the mean or Gaussian-weighted mean intensity of its neighbourhood. OpenCV's `adaptiveThreshold` function implements this approach, and SmartGrader employs it with a Gaussian weighting and a block size calibrated to the expected bubble diameter. This ensures robust binarisation even when the scanned image exhibits significant variations in brightness across its extent.

## 2.7 Vision Language Models

Vision Language Models (VLMs) represent a recent and rapidly evolving class of multimodal artificial intelligence models that can jointly process visual and textual inputs. Unlike traditional computer vision models that produce fixed-category outputs, VLMs generate free-form natural language responses conditioned on both an image and a text prompt, enabling them to perform tasks such as image description, visual question answering, optical character recognition, and document understanding.

### 2.7.1 LLaVA

LLaVA (Large Language and Vision Assistant), introduced by Liu et al. [@liu2023llava], was among the first open-source VLMs to demonstrate strong performance on visual instruction-following tasks. LLaVA connects a pre-trained CLIP visual encoder to a large language model (LLaMA) through a simple linear projection layer. The model is trained in two stages: first, a pre-training phase that aligns visual and textual representations using image-caption pairs; and second, a fine-tuning phase using instruction-following data that teaches the model to respond to complex visual questions.

LLaVA established the architectural template that subsequent VLMs would follow: a frozen or partially frozen visual encoder, a projection module that maps visual tokens into the language model's embedding space, and a language model backbone that generates the response. Its open-source release catalysed rapid progress in the field.

### 2.7.2 Qwen2-VL Family

The Qwen2-VL family, developed by Alibaba Cloud and described by Wang et al. [@wang2024qwen2vl], represents a significant advance in VLM capability, particularly for multilingual and document understanding tasks. The Qwen2-VL architecture introduces a Naive Dynamic Resolution mechanism that allows the model to process images of arbitrary resolution by dynamically dividing them into a variable number of visual tokens, rather than resizing all inputs to a fixed resolution. This is particularly advantageous for document understanding tasks where fine-grained details such as handwritten characters must be preserved.

The Qwen2.5-VL-3B-Instruct variant, which SmartGrader employs, offers a compelling balance between capability and resource efficiency. With 3 billion parameters and 4-bit quantisation via the BitsAndBytes library [@dettmers2022llmint8], the model requires approximately 4--6 GB of GPU VRAM, making it deployable on consumer-grade graphics cards such as the NVIDIA RTX 3060 or RTX 4060. Despite its modest size, Qwen2.5-VL-3B demonstrates strong performance on OCR benchmarks and supports Arabic, French, and English text recognition -- the three languages most commonly encountered in Algerian educational contexts.

### 2.7.3 PaliGemma

PaliGemma, introduced by Beyer et al. [@beyer2024paligemma], is a 3-billion-parameter VLM developed by Google that combines the SigLIP visual encoder with the Gemma language model. PaliGemma is designed as a versatile transfer model, achieving strong performance across a wide range of visual-linguistic tasks after fine-tuning. Its architecture emphasises efficiency, with the visual encoder producing a compact set of tokens that are prepended to the language model's input sequence.

While PaliGemma achieves competitive results on standard benchmarks, its OCR capabilities for handwritten text in non-Latin scripts are less developed than those of the Qwen2-VL family, which benefits from extensive multilingual pre-training data. Additionally, PaliGemma's fine-tuning-oriented design means that it requires task-specific adaptation to achieve optimal performance, whereas Qwen2.5-VL-3B-Instruct can be used effectively in a zero-shot or few-shot prompting regime.

### 2.7.4 GPT-4V

GPT-4V (GPT-4 with Vision), developed by OpenAI, represents the current state of the art in VLM capability. GPT-4V demonstrates exceptional performance on visual question answering, OCR, document understanding, and complex visual reasoning tasks. However, GPT-4V is a proprietary, cloud-based model accessible only through a paid API, with per-token pricing that would render large-scale examination grading prohibitively expensive. Furthermore, the transmission of student examination data to an external cloud service raises significant privacy and data sovereignty concerns, particularly in the context of Algerian educational institutions subject to national data protection regulations.

### 2.7.5 Comparison of Vision Language Models

| Model | Parameters | Open Source | Multilingual OCR | Min. VRAM (4-bit) | API Cost |
|-------|-----------|-------------|-------------------|-------------------|----------|
| LLaVA-1.5-7B | 7B | Yes | Limited | ~6 GB | Free |
| Qwen2.5-VL-3B | 3B | Yes | Strong (AR/FR/EN) | ~4 GB | Free |
| PaliGemma-3B | 3B | Yes | Moderate | ~4 GB | Free |
| GPT-4V | Unknown | No | Excellent | N/A (cloud) | ~\$0.01/image |

## 2.8 Handwriting Recognition

Handwriting recognition -- the conversion of handwritten text in images to machine-encoded text -- is a prerequisite for the automated grading of short-answer examination questions. This section reviews the principal approaches to handwriting recognition, ranging from classical OCR engines to modern VLM-based methods.

### 2.8.1 Tesseract OCR

Tesseract, originally developed by Hewlett-Packard and subsequently maintained by Google, is the most widely deployed open-source OCR engine [@smith2007ocr]. Tesseract 4.0 and later versions employ a Long Short-Term Memory (LSTM) neural network for text line recognition, achieving strong performance on printed text. However, Tesseract's accuracy degrades significantly on handwritten text, particularly for cursive scripts and non-Latin writing systems such as Arabic. The engine requires clean, well-segmented input images and is sensitive to noise, skew, and variations in handwriting style.

### 2.8.2 EasyOCR

EasyOCR is a Python-based OCR library that supports over 80 languages, including Arabic and French. It employs a CRAFT (Character Region Awareness for Text Detection) network for text detection and a ResNet-based sequence-to-sequence model for recognition. EasyOCR offers improved handling of handwritten text compared to Tesseract, but its accuracy on heavily cursive or stylistically diverse handwriting remains limited. The library is straightforward to integrate into Python applications and supports GPU acceleration.

### 2.8.3 TrOCR

TrOCR (Transformer-based OCR) is a model developed by Microsoft that applies the Transformer architecture to optical character recognition. TrOCR uses a pre-trained image Transformer (BEiT or DeiT) as an encoder and a pre-trained language model as a decoder, framing OCR as an image-to-text sequence generation task. TrOCR achieves state-of-the-art results on printed and handwritten English text benchmarks. However, its support for Arabic script is limited, and deployment requires fine-tuning on domain-specific data to achieve acceptable accuracy on the diverse handwriting styles encountered in examination settings.

### 2.8.4 VLM-Based OCR

The most recent approach to handwriting recognition leverages Vision Language Models as general-purpose document readers. Rather than employing a dedicated OCR pipeline, the VLM receives a scanned image and a text prompt instructing it to transcribe the handwritten content. This approach offers several advantages: it requires no task-specific training, it can handle mixed-language text seamlessly, and it benefits from the VLM's broader understanding of document structure and context.

SmartGrader adopts this VLM-based approach using the Qwen2.5-VL-3B-Instruct model. The model receives the full scanned page image together with a carefully engineered prompt that instructs it to identify and transcribe the student's handwritten response for a specific question. This full-page approach, as opposed to cropping individual answer regions, allows the model to leverage spatial context (such as question numbering) to locate and attribute responses accurately.

### 2.8.5 Comparison of Handwriting Recognition Approaches

| Approach | Arabic Support | Handwriting Accuracy | Setup Complexity | GPU Required |
|----------|---------------|---------------------|-----------------|-------------|
| Tesseract | Partial | Low | Low | No |
| EasyOCR | Yes | Moderate | Low | Optional |
| TrOCR | Limited | High (English) | High (fine-tuning) | Yes |
| VLM-based (Qwen2.5-VL) | Yes | High | Low (prompt only) | Yes |

## 2.9 Retrieval-Augmented Generation for LLM Improvement

Retrieval-Augmented Generation (RAG), introduced by Lewis et al. [@lewis2020rag], is a technique that enhances the performance of language models by augmenting their input with relevant information retrieved from an external knowledge base. In the standard RAG framework, a retriever module identifies documents relevant to the input query, and these documents are prepended to the language model's prompt, providing additional context that guides the model's generation.

The core insight of RAG is that language models, despite their extensive pre-training knowledge, can benefit significantly from task-specific contextual information provided at inference time. This is particularly relevant for grading tasks, where the model must evaluate student responses against specific criteria that vary from one examination to another.

### 2.9.1 RAG in the Context of Exam Grading

SmartGrader adapts the RAG paradigm to the examination grading context through a teacher correction feedback loop. When the AI model evaluates a student's answer and the teacher disagrees with the assigned score, the teacher provides a correction comprising the correct score and optional feedback. This correction is stored in the `ai_corrections` database table, associated with the relevant question.

On subsequent evaluations of the same question, the system retrieves all stored corrections for that question and injects them into the model's prompt as few-shot examples. Each example consists of a student's handwritten response text, the teacher-assigned score, and the teacher's feedback. This mechanism allows the model to calibrate its grading behaviour to the teacher's expectations without requiring any parameter updates or fine-tuning.

### 2.9.2 Few-Shot In-Context Learning

The effectiveness of the RAG feedback loop relies on the in-context learning capability of modern language models -- their ability to adapt their behaviour based on examples provided in the prompt. Research has demonstrated that large language models can achieve significant performance improvements when provided with even a small number of task-specific examples, a phenomenon known as few-shot learning.

In SmartGrader's implementation, the number of retrieved corrections is bounded to avoid exceeding the model's context window. The most recent corrections are prioritised, as they represent the teacher's most current grading standards. Empirical evaluation (presented in Chapter 5) demonstrates that grading accuracy improves measurably after as few as three to five corrections per question.

### 2.9.3 Prompt Engineering

Prompt engineering -- the systematic design of input prompts to elicit desired model behaviour -- is a critical component of SmartGrader's AI pipeline. The system employs two distinct prompt templates:

- **OCR Prompt:** Instructs the model to examine the scanned page image and transcribe the student's handwritten answer for a specified question. The prompt emphasises accuracy and requests the transcription in the original language of the response.

- **Evaluation Prompt:** Provides the model with the question text, the model answer, optional keywords, the student's transcribed response, and any retrieved corrections. The prompt instructs the model to assign a score on a defined scale and to provide a brief justification for the assigned score.

Both prompts are engineered to produce structured, parseable output that the system can process programmatically, reducing the need for complex post-processing of the model's natural language responses.

## 2.10 Comparative Synthesis

The following table synthesises the capabilities of existing solutions and positions SmartGrader relative to the state of the art across an extended set of evaluation criteria:

| Criterion | Remark OMR | GradeCam | ZipGrade | Moodle | ExamSoft | ProctorU | GPT-4V | **SmartGrader** |
|-----------|-----------|----------|----------|--------|----------|----------|--------|----------------|
| MCQ scanning | Yes | Yes | Yes | No | No | No | No | **Yes** |
| Handwriting OCR | No | No | No | No | No | No | Yes | **Yes** |
| AI-based grading | No | No | No | No | No | No | Yes | **Yes** |
| RAG feedback loop | No | No | No | No | No | No | No | **Yes** |
| Online exam engine | No | No | No | Yes | Yes | No | No | **Yes** |
| Student groups | No | No | No | Yes | Yes | No | No | **Yes** |
| Browser proctoring | No | No | No | No | Partial | Yes | No | **Yes** |
| Face detection (client) | No | No | No | No | No | Yes | No | **Yes** |
| JWT authentication | No | No | No | No | Yes | Yes | N/A | **Yes** |
| Multilingual (AR/FR/EN) | No | No | No | Partial | No | N/A | Yes | **Yes** |
| Open source | No | No | No | Yes | No | No | No | **Yes** |
| Local deployment | Yes | No | Yes | Yes | No | No | No | **Yes** |
| Docker support | No | No | No | Yes | No | No | No | **Yes** |
| Web interface | No | Yes | No | Yes | Yes | Yes | Yes | **Yes** |

This synthesis reveals that no existing solution simultaneously offers all capabilities. Commercial OMR systems lack AI grading, online delivery, and proctoring. Online examination platforms lack paper scanning and AI grading. Proctoring solutions depend on proprietary cloud infrastructure. GPT-4V, while capable on AI tasks, is proprietary and cloud-dependent. SmartGrader is designed to fill this gap by unifying all dimensions of examination management in a single, locally deployable, open-source platform.

## 2.11 Identified Gaps and Justification

The literature review and technology survey presented in this chapter reveal several significant gaps in the current landscape of automated grading and online examination solutions:

1. **No unified MCQ + short-answer + online grading system.** Existing OMR solutions handle only multiple-choice questions, while AI-based grading tools typically operate only on digital text. Online examination platforms lack paper scanning. No widely available system combines all three modalities in a single integrated platform.

2. **Limited multilingual handwriting support.** Most OCR engines and even some VLMs struggle with Arabic handwriting, which presents unique challenges due to its cursive nature, right-to-left directionality, and contextual letter forms. Algerian educational contexts require robust support for Arabic, French, and potentially Tamazight scripts.

3. **No teacher feedback integration.** Existing automated grading systems operate as static pipelines. None incorporate a mechanism for the teacher to correct the system's errors and for those corrections to improve subsequent evaluations.

4. **Cloud dependency and cost barriers.** The most capable AI models and proctoring services are available only through cloud APIs with per-request or per-session pricing, making them impractical for large-scale institutional use. A locally deployable solution addresses both cost and data privacy concerns.

5. **Privacy-invasive proctoring.** Existing proctoring solutions transmit continuous video streams to cloud servers, raising significant privacy and data sovereignty concerns. A browser-native approach that performs face detection locally and transmits only discrete snapshots addresses these concerns without sacrificing monitoring capability.

6. **Lack of open-source alternatives.** While individual components are freely available, no project has combined MCQ scanning, AI grading, online examination delivery, and browser-based proctoring in a cohesive, well-documented, and deployable system.

SmartGrader addresses each of these gaps. It combines computer vision-based MCQ scanning with VLM-based handwriting recognition, semantic grading, a complete online examination engine, browser-native proctoring using TensorFlow.js BlazeFace, JWT authentication, and flexible deployment modes. It runs entirely on local hardware, requires only a consumer-grade GPU for AI features, and is released as an open-source project with comprehensive documentation.
