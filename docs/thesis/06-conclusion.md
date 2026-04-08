# Chapter 6: Conclusion and Perspectives

## 6.1 Summary

This thesis has presented SmartGrader, an integrated web-based platform for examination management that combines classical computer vision techniques, modern vision-language model capabilities, a fully online examination engine, browser-native academic integrity monitoring, and flexible production deployment configurations. The project was developed across four incremental phases, each building upon the preceding one to produce a complete, production-ready application.

**Phase 1: Authentication and Role Management.** The system was secured with JWT-based authentication supporting teacher and student roles. User accounts are managed through a `users` table with bcrypt-hashed passwords. Route decorators (`@require_auth`, `@require_role`) enforce access control at the endpoint level. Students can authenticate via barcode scan of their matricule card. Bulk student import via CSV enables rapid population of the student registry. The automated test suite grew from its foundation with 28 dedicated authentication tests.

**Phase 2: Online Examination Engine.** A complete online examination subsystem was implemented on top of the authenticated backend. This phase introduced student group management, exam session scheduling with configurable start times and durations, a student-facing timed examination interface with immediate answer persistence, auto-submission on timer expiry (enforced both client-side and server-side), and a teacher monitoring dashboard for real-time session oversight. The system correctly handles network interruptions (via server-side answer persistence), concurrent sessions (multiple independent sessions with isolated attempt records), and automatic MCQ grading on submission.

**Phase 3: Anti-Cheat and Proctoring.** A browser-native proctoring layer was integrated into the student examination interface. The ProctorEngine employs TensorFlow.js and the BlazeFace model to perform face presence detection at 1-second intervals entirely within the browser, without transmitting video to any server. Browser integrity events (tab switch, fullscreen exit, window blur, copy-paste) are tracked and reported. Periodic JPEG snapshots are captured and stored server-side. A warning escalation system automatically terminates the attempt after a configurable number of violations. A dedicated teacher dashboard displays live student status, event timelines, and snapshots.

**Phase 4: Deployment and Infrastructure.** The application was prepared for three production deployment modes: LAN mode (Gunicorn multi-worker server for classroom and departmental use), university server mode (Gunicorn behind Nginx with SSL/TLS termination and hardened CORS policy), and Docker Compose mode (containerised deployment for portable institutional use). Configuration management supports environment-specific settings via the existing `Config` class hierarchy.

The original sub-projects from the project's foundation remain fully operational:

**Sub-Project 1: Architecture and Backend.** The layered Flask architecture with SQLAlchemy ORM, service layer, and blueprint-based routing provides the foundation for all subsequent phases. The database has grown from 7 to 15 tables to accommodate authentication, session management, and proctoring.

**Sub-Project 2: Scanner and Frontend.** The five-stage MCQ scanner pipeline achieves 92.5% end-to-end grading accuracy. The React frontend now comprises 13 pages covering all functional areas from paper scanning to online examination delivery.

**Sub-Project 3: AI Integration.** The Qwen2.5-VL-3B-Instruct vision-language model performs handwritten text recognition and AI-assisted answer evaluation with a RAG feedback loop. The AI pipeline achieves 85% exact-match accuracy after 20 teacher corrections.

The automated test suite has grown to 191 tests across 8 modules, providing comprehensive regression protection across all architectural layers.

## 6.2 Limitations

Despite the achievements described above, SmartGrader is subject to several limitations that constrain its applicability in certain scenarios:

1. **Model size.** The 3-billion parameter vision-language model provides adequate performance for short-answer questions but may lack the reasoning capacity required for complex, multi-part responses. The model occasionally produces incorrect scores for answers that are semantically correct but expressed in unexpected formulations.

2. **Arabic handwriting.** While the Qwen2.5-VL model supports Arabic text, its OCR accuracy for Arabic handwriting is lower than for French and English, particularly for connected cursive script. This remains a significant limitation in the Algerian educational context.

3. **Single GPU requirement.** AI grading requires a CUDA-compatible GPU and does not support CPU-only inference or multi-GPU parallelism, limiting throughput for high-volume grading scenarios.

4. **No essay-length support.** The system targets short-answer questions (one to three sentences). Essay-length responses exceed the current model's context window and would require a different evaluation approach.

5. **Scanner sensitivity.** The OMR pipeline assumes clean printing and scanning conditions. Accuracy degrades with low-resolution scans, poor print quality, or significant page distortion.

6. **Proctoring false positives.** BlazeFace may occasionally fail to detect a face that is present (e.g., when the student adjusts their position). The configurable warning threshold partially mitigates this, but a formal false positive characterisation study is needed.

7. **SQLite scalability.** SQLite performs well for single-machine deployments but may become a bottleneck under high concurrency. University-scale deployments serving hundreds of simultaneous students would benefit from migration to PostgreSQL.

## 6.3 Future Work

Several directions for future development would address the identified limitations and extend the system's capabilities:

1. **LoRA fine-tuning.** Low-Rank Adaptation (LoRA) fine-tuning of the vision-language model on a curated dataset of Algerian exam papers would improve both OCR accuracy (particularly for Arabic handwriting) and grading alignment with local pedagogical standards. LoRA requires significantly fewer computational resources than full fine-tuning and can be performed on a single consumer GPU.

2. **Larger models.** As GPU hardware becomes more accessible, migrating to larger models in the Qwen2-VL family (7B, 14B, or 72B parameters) would improve reasoning depth and grading accuracy. The lazy loading architecture already supports model swapping via the `VISION_MODEL` configuration parameter.

3. **Mobile application.** A React Native mobile application would enable teachers to photograph answer sheets directly with their smartphone cameras, eliminating the need for a separate scanner. The camera-based workflow would require additional image preprocessing (perspective correction, illumination normalisation) to compensate for less controlled capture conditions.

4. **Essay grading.** Extending the AI pipeline to support essay-length responses would require a multi-stage evaluation approach: structural analysis (introduction, body, conclusion), argument coherence assessment, rubric-based scoring, and detailed feedback generation. This would necessitate a larger model with an extended context window or a chunking strategy that evaluates the essay in segments.

5. **Advanced proctoring.** The current proctoring system detects face presence and browser events. Future work could incorporate gaze estimation (using MediaPipe FaceMesh) to detect when the student looks away from the screen, and audio analysis to detect speech that might indicate collaboration. These would require additional privacy safeguards and informed consent mechanisms.

6. **PostgreSQL migration.** For university-scale deployments, migrating from SQLite to PostgreSQL would provide better concurrent write performance, row-level locking, and connection pooling. The SQLAlchemy ORM layer already abstracts the database, making this migration straightforward via the `SQLALCHEMY_DATABASE_URI` configuration parameter.

7. **Multi-page examination support.** The current scanner processes single-page answer sheets. Supporting multi-page examinations would require page sequencing, cross-page answer continuation detection, and a modified grid mapping algorithm.

8. **Real-time notifications.** Replacing the teacher dashboard's polling architecture with a WebSocket-based push notification system (e.g., via Flask-SocketIO) would reduce latency in event visibility from 5 seconds to near-real-time, providing a more responsive monitoring experience during large examination sessions.

These future directions represent a natural evolution of the SmartGrader platform from its current state as a comprehensive single-institution tool toward a scalable, feature-rich educational assessment platform. The clean layered architecture established across all four phases provides a solid foundation for implementing these extensions incrementally.
