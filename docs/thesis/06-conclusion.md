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
