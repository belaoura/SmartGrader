import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight, Send, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  useStartAttempt,
  useExamStatus,
  useSaveAnswer,
  useSaveAnswersBatch,
  useSubmitExam,
} from "@/hooks/use-student-exam";
import ProctorEngine from "@/components/ProctorEngine";
import FullscreenLockdown from "@/components/FullscreenLockdown";
import ProctorWarningBanner from "@/components/ProctorWarningBanner";

function formatTime(seconds) {
  if (seconds < 0) seconds = 0;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export default function TakeExam() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [questions, setQuestions] = useState([]);
  const [sessionConfig, setSessionConfig] = useState(null);
  const [examData, setExamData] = useState(null);
  const [answers, setAnswers] = useState({}); // questionId -> choiceId
  const [currentIndex, setCurrentIndex] = useState(0);
  const [remainingSeconds, setRemainingSeconds] = useState(null);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const startAttempt = useStartAttempt();
  const saveAnswer = useSaveAnswer();
  const saveAnswersBatch = useSaveAnswersBatch();
  const submitExam = useSubmitExam();

  // Start attempt on mount
  useEffect(() => {
    startAttempt.mutate(sessionId, {
      onSuccess: (data) => {
        setQuestions(data.questions || []);
        setSessionConfig(data.session || data);
        setExamData(data);
        setRemainingSeconds(data.remaining_seconds ?? null);
        setStarted(true);
      },
      onError: (err) => {
        setError(err.message || "Failed to start exam.");
      },
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  // Sync remaining_seconds from server status every 30s
  const statusEnabled = started && remainingSeconds !== null && !submitted;
  const { data: statusData } = useExamStatus(sessionId, statusEnabled);
  useEffect(() => {
    if (statusData?.remaining_seconds != null) {
      setRemainingSeconds(statusData.remaining_seconds);
    }
  }, [statusData]);

  // Local countdown
  useEffect(() => {
    if (!started || remainingSeconds === null || submitted) return;
    const interval = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [started, submitted]);

  // Periodic auto-save (auto_periodic mode: every 30s)
  const answersRef = useRef(answers);
  answersRef.current = answers;
  useEffect(() => {
    if (!started || submitted) return;
    const mode = sessionConfig?.save_mode;
    if (mode !== "auto_periodic") return;
    const interval = setInterval(() => {
      const pending = Object.entries(answersRef.current).map(([qId, cId]) => ({
        question_id: Number(qId),
        choice_id: Number(cId),
      }));
      if (pending.length === 0) return;
      saveAnswersBatch.mutate({ sessionId, answers: pending });
    }, 30000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [started, submitted, sessionConfig]);

  const handleSelectChoice = useCallback(
    (questionId, choiceId) => {
      setAnswers((prev) => ({ ...prev, [questionId]: choiceId }));
      const mode = sessionConfig?.save_mode;
      if (mode === "auto_each") {
        saveAnswer.mutate({ sessionId, questionId, choiceId });
      }
    },
    [sessionConfig, sessionId, saveAnswer]
  );

  const handleManualSave = () => {
    const pending = Object.entries(answers).map(([qId, cId]) => ({
      question_id: Number(qId),
      choice_id: Number(cId),
    }));
    if (pending.length === 0) return;
    saveAnswersBatch.mutate({ sessionId, answers: pending });
  };

  const handleAutoSubmit = () => {
    if (submitted) return;
    submitExam.mutate(sessionId, {
      onSuccess: () => {
        setSubmitted(true);
        navigate(`/exam/${sessionId}/result`);
      },
    });
  };

  const handleSubmit = () => {
    if (!window.confirm("Are you sure you want to submit your exam? This cannot be undone.")) return;
    // Final batch save for manual/periodic modes
    const mode = sessionConfig?.save_mode;
    if (mode === "auto_periodic" || mode === "manual") {
      const pending = Object.entries(answers).map(([qId, cId]) => ({
        question_id: Number(qId),
        choice_id: Number(cId),
      }));
      if (pending.length > 0) {
        saveAnswersBatch.mutate(
          { sessionId, answers: pending },
          {
            onSuccess: () => {
              submitExam.mutate(sessionId, {
                onSuccess: () => {
                  setSubmitted(true);
                  navigate(`/exam/${sessionId}/result`);
                },
              });
            },
          }
        );
        return;
      }
    }
    submitExam.mutate(sessionId, {
      onSuccess: () => {
        setSubmitted(true);
        navigate(`/exam/${sessionId}/result`);
      },
    });
  };

  // Loading state
  if (!started && !error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-muted-foreground">Loading exam...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="text-destructive text-lg">{error}</div>
        <Button variant="outline" onClick={() => navigate("/exam")}>Back to Dashboard</Button>
      </div>
    );
  }

  const displayMode = sessionConfig?.display_mode || "all_at_once";
  const saveMode = sessionConfig?.save_mode || "auto_each";
  const isLowTime = remainingSeconds !== null && remainingSeconds < 300;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="space-y-4 max-w-4xl">
      {/* Proctoring components */}
      {examData?.proctoring_enabled && (
        <ProctorEngine sessionId={sessionId} onError={(msg) => setError(msg)} />
      )}
      {examData?.lockdown_enabled && (
        <FullscreenLockdown onViolation={() => {}} />
      )}
      {examData?.proctoring_enabled && examData?.cheat_response !== "log_only" && (
        <ProctorWarningBanner sessionId={sessionId} onCaptureRequest={() => {}} />
      )}

      {/* Header bar */}
      <div className="flex items-center justify-between sticky top-20 z-30 bg-background/90 backdrop-blur-sm py-3 px-4 rounded-xl border border-border shadow-sm">
        <div className="font-semibold text-sm truncate">
          {sessionConfig?.exam_title || "Exam"}
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-muted-foreground">
            {answeredCount}/{questions.length} answered
          </span>
          {remainingSeconds !== null && (
            <span className={`font-mono font-bold text-sm ${isLowTime ? "text-red-500" : "text-foreground"}`}>
              {formatTime(remainingSeconds)}
            </span>
          )}
          {saveMode === "manual" && (
            <Button size="sm" variant="outline" onClick={handleManualSave} disabled={saveAnswersBatch.isPending}>
              <Save className="mr-1.5 h-3.5 w-3.5" /> Save
            </Button>
          )}
          <Button
            size="sm"
            onClick={handleSubmit}
            disabled={submitExam.isPending || submitted}
            className="cursor-pointer"
          >
            <Send className="mr-1.5 h-3.5 w-3.5" /> Submit
          </Button>
        </div>
      </div>

      {/* Question navigator */}
      <div className="flex flex-wrap gap-2 p-3 bg-muted/30 rounded-xl border border-border">
        {questions.map((q, idx) => {
          const isAnswered = answers[q.id] != null;
          const isCurrent = displayMode === "one_by_one" && idx === currentIndex;
          return (
            <button
              key={q.id}
              onClick={() => displayMode === "one_by_one" && setCurrentIndex(idx)}
              className={[
                "h-8 w-8 rounded text-xs font-medium border transition-colors",
                isCurrent
                  ? "bg-primary text-primary-foreground border-primary"
                  : isAnswered
                  ? "bg-green-500/15 text-green-600 dark:text-green-400 border-green-500/30"
                  : "bg-background text-muted-foreground border-border hover:bg-accent/50",
                displayMode === "one_by_one" ? "cursor-pointer" : "cursor-default",
              ].join(" ")}
            >
              {idx + 1}
            </button>
          );
        })}
      </div>

      {/* Questions */}
      {displayMode === "all_at_once" ? (
        <div className="space-y-6">
          {questions.map((q, idx) => (
            <QuestionCard
              key={q.id}
              question={q}
              index={idx}
              selectedChoiceId={answers[q.id]}
              onSelect={(choiceId) => handleSelectChoice(q.id, choiceId)}
            />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {questions.length > 0 && (
            <QuestionCard
              question={questions[currentIndex]}
              index={currentIndex}
              selectedChoiceId={answers[questions[currentIndex]?.id]}
              onSelect={(choiceId) => handleSelectChoice(questions[currentIndex].id, choiceId)}
            />
          )}
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="mr-1 h-4 w-4" /> Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              {currentIndex + 1} / {questions.length}
            </span>
            <Button
              variant="outline"
              onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}
              disabled={currentIndex === questions.length - 1}
            >
              Next <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function QuestionCard({ question, index, selectedChoiceId, onSelect }) {
  return (
    <Card className="glass">
      <CardContent className="pt-4 space-y-4">
        <p className="font-medium leading-relaxed">
          <span className="text-muted-foreground mr-2">{index + 1}.</span>
          {question.text}
        </p>
        <div className="space-y-2">
          {(question.choices || []).map((choice) => {
            const selected = selectedChoiceId === choice.id;
            return (
              <button
                key={choice.id}
                onClick={() => onSelect(choice.id)}
                className={[
                  "w-full text-left rounded-lg border px-4 py-2.5 text-sm transition-all duration-150",
                  selected
                    ? "border-primary bg-primary/10 text-primary font-medium"
                    : "border-border bg-background hover:border-primary/50 hover:bg-accent/30",
                ].join(" ")}
              >
                <span className="font-mono text-xs mr-2 text-muted-foreground">
                  {String.fromCharCode(65 + (question.choices || []).indexOf(choice))}.
                </span>
                {choice.text}
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
