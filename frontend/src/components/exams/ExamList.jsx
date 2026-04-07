import { useNavigate } from "react-router-dom";
import { Trash2, Printer, ChevronRight, Calendar, HelpCircle, Award } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDeleteExam } from "@/hooks/use-exams";

export default function ExamList({ exams }) {
  const navigate = useNavigate();
  const deleteExam = useDeleteExam();

  const handleDelete = (e, id) => {
    e.stopPropagation();
    if (window.confirm("Delete this exam and all its questions?")) {
      deleteExam.mutate(id);
    }
  };

  const handlePrint = async (e, exam) => {
    e.stopPropagation();
    try {
      const res = await fetch(`/api/exams/${exam.id}/questions`);
      const questions = await res.json();
      if (!questions?.length) {
        alert("No questions in this exam yet.");
        return;
      }

      const questionsPerPage = 8;
      const pages = [];
      for (let i = 0; i < questions.length; i += questionsPerPage) {
        pages.push(questions.slice(i, i + questionsPerPage));
      }
      const totalPages = pages.length;

      const generateQuestionHtml = (q, globalIndex) => {
        const optionsHtml = q.choices?.map((c) =>
          `<div class="option"><div class="circle"></div><div class="option-text">${c.text}</div></div>`
        ).join("") || "";
        return `<div class="question"><div class="q-text"><span class="q-number">${globalIndex + 1}.</span><span class="q-text-content">${q.question_text}</span></div><div class="options">${optionsHtml}</div></div>`;
      };

      const nameBoxes = (n) => Array(n).fill('<span class="name-box"></span>').join("");
      const idBoxes = (n) => Array(n).fill('<span class="id-box"></span>').join("");

      const pagesHtml = pages.map((pq, pi) => {
        const si = pi * questionsPerPage;
        const mid = Math.ceil(pq.length / 2);
        const left = pq.slice(0, mid).map((q, i) => generateQuestionHtml(q, si + i)).join("");
        const right = pq.slice(mid).map((q, i) => generateQuestionHtml(q, si + mid + i)).join("");
        const isFirst = pi === 0;

        const header = isFirst ? `<div class="header">
          <div class="header-row"><div class="header-label">INSTITUTION:</div><div class="underline">___________________________</div></div>
          <div class="header-row"><div class="header-label">DEPARTMENT:</div><div class="underline">___________________________</div></div>
          <div class="header-row"><div class="header-label">EXAM:</div><div class="underline">${exam.title || ""}</div></div>
          <div class="header-row"><div class="header-label">SUBJECT:</div><div class="underline">${exam.subject || ""}</div></div>
          <div class="header-row"><div class="header-label">DATE:</div><div class="underline">${exam.date || ""}</div></div>
        </div>` : `<div class="header minimal"><div class="header-row"><div class="header-label">EXAM CONTINUED — PAGE ${pi + 1}</div></div></div>`;

        return `<div class="page">
          <div class="align top-left"></div><div class="align top-right"></div><div class="align bottom-left"></div><div class="align bottom-right"></div>
          <div class="page-content">
            ${header}
            <div class="student-section">
              <div class="qr-area"><div class="qr-placeholder"><div class="qr-corner"></div><div class="qr-corner"></div><div class="qr-corner"></div><div class="qr-corner"></div><div class="qr-label">ID</div></div></div>
              <div class="info-row"><div class="info-label">LAST NAME:</div><div class="box-row">${nameBoxes(20)}</div></div>
              <div class="info-row"><div class="info-label">FIRST NAME:</div><div class="box-row">${nameBoxes(18)}</div></div>
              <div class="info-row"><div class="info-label">STUDENT ID:</div><div class="box-row">${idBoxes(14)}</div></div>
            </div>
            ${isFirst ? '<div class="instruction-text">✦ CHOOSE THE CORRECT ANSWER FOR EACH QUESTION ✦</div>' : ''}
            <div class="questions-markers-top"><div class="section-marker"></div><div class="section-marker"></div></div>
            <div class="questions-grid"><div class="vertical-divider"></div><div class="column">${left}</div><div class="column">${right}</div></div>
            <div class="questions-markers-bottom"><div class="section-marker"></div><div class="section-marker"></div></div>
            <div class="page-number">Page ${pi + 1} of ${totalPages}</div>
          </div>
        </div>`;
      }).join("");

      const win = window.open("", "_blank");
      win.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>QCM - ${exam.title}</title>
        <style>
          @page{size:A4;margin:0}*{margin:0;padding:0;box-sizing:border-box}body{font-family:"Times New Roman",serif;background:white;width:210mm;-webkit-print-color-adjust:exact;print-color-adjust:exact}
          .page{width:210mm;height:297mm;position:relative;background:white;page-break-after:always;break-after:page;margin:0 auto;padding:8mm 12mm;overflow:hidden}
          .page-content{width:100%;height:100%;display:flex;flex-direction:column;overflow:hidden}
          .header{border:1pt solid black;padding:2mm 3mm;margin-bottom:2mm;flex-shrink:0}.header.minimal{border:1pt dashed black;padding:1.5mm 2mm;text-align:center}
          .header-row{display:flex;align-items:flex-end;margin-bottom:1.5mm;height:4.5mm}.header-label{font-weight:bold;min-width:25mm;margin-right:2mm;font-size:9pt}.underline{flex:1;border-bottom:0.5pt solid black;height:3.5mm;margin-bottom:0.5mm;font-size:9pt;padding-left:2mm}
          .student-section{border:1pt solid black;padding:2.5mm 3mm;margin-bottom:2mm;position:relative;min-height:36mm;flex-shrink:0}
          .qr-area{position:absolute;top:2.5mm;right:3mm;width:17mm;height:17mm;border:0.5pt solid black;display:flex;justify-content:center;align-items:center}
          .qr-placeholder{width:100%;height:100%;position:relative}.qr-corner{position:absolute;width:2.5mm;height:2.5mm;border:0.3mm solid #666}
          .qr-corner:nth-child(1){top:1.5mm;left:1.5mm;border-right:none;border-bottom:none}.qr-corner:nth-child(2){top:1.5mm;right:1.5mm;border-left:none;border-bottom:none}
          .qr-corner:nth-child(3){bottom:1.5mm;left:1.5mm;border-right:none;border-top:none}.qr-corner:nth-child(4){bottom:1.5mm;right:1.5mm;border-left:none;border-top:none}
          .qr-label{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:10pt;font-weight:bold;color:#666}
          .info-row{margin-bottom:2mm;width:calc(100% - 21mm);max-width:140mm}.info-row:last-child{margin-bottom:0}
          .info-label{font-weight:bold;margin-bottom:0.3mm;font-size:8.5pt;text-transform:uppercase}.box-row{display:flex;gap:0.5mm;flex-wrap:wrap}
          .name-box{width:3.8mm;height:3.8mm;border:0.5pt solid black;display:inline-block}.id-box{width:4.3mm;height:4.3mm;border:0.5pt solid black;display:inline-block}
          .instruction-text{text-align:center;font-size:9pt;font-weight:bold;font-style:italic;margin-bottom:2mm;padding:1mm;background-color:#f9f9f9;border-left:2pt solid #333;border-right:2pt solid #333;color:#333;letter-spacing:0.3px;text-transform:uppercase;flex-shrink:0}
          .questions-grid{display:grid;grid-template-columns:1fr 1fr;column-gap:5mm;position:relative;flex:1 1 0;min-height:0;overflow:hidden}
          .vertical-divider{position:absolute;top:0;bottom:0;left:calc(50% - 2.5mm);width:0.5pt;background:black;pointer-events:none}
          .column{display:flex;flex-direction:column;overflow:hidden;min-width:0}
          .question{margin-bottom:2.5mm;padding-bottom:0.5mm;border-bottom:1pt solid #000;break-inside:avoid;page-break-inside:avoid;flex-shrink:0}.question:last-child{border-bottom:none;margin-bottom:0}
          .q-text{font-weight:bold;margin-bottom:1mm;line-height:4.3mm;font-size:9pt;display:flex;gap:1.5mm;align-items:flex-start;word-wrap:break-word;overflow-wrap:break-word}
          .q-number{font-weight:bold;min-width:6.5mm;flex-shrink:0;font-size:9pt;white-space:nowrap}.q-text-content{flex:1;word-wrap:break-word;overflow-wrap:break-word}
          .options{display:flex;flex-direction:column;gap:1mm;margin-left:8mm;width:calc(100% - 8mm)}
          .option{display:flex;align-items:flex-start;gap:1.2mm;font-size:9pt;word-wrap:break-word;overflow-wrap:break-word}
          .circle{min-width:2.8mm;width:2.8mm;height:2.8mm;border:0.5pt solid black;border-radius:50%;flex-shrink:0;background:white;margin-top:0.5mm}
          .option-text{flex:1;min-width:0;line-height:4.3mm;font-size:9pt;word-wrap:break-word;overflow-wrap:break-word}
          .align{position:absolute;width:3mm;height:3mm;background:black;z-index:10}.align.top-left{top:2mm;left:2mm}.align.top-right{top:2mm;right:2mm}.align.bottom-left{bottom:2mm;left:2mm}.align.bottom-right{bottom:2mm;right:2mm}
          .questions-markers-top,.questions-markers-bottom{display:flex;justify-content:space-between;padding:0 2mm;flex-shrink:0}.section-marker{width:0;height:0}
          .questions-markers-top .section-marker{border-left:4mm solid transparent;border-right:4mm solid transparent;border-top:6mm solid black}
          .questions-markers-bottom .section-marker{border-left:4mm solid transparent;border-right:4mm solid transparent;border-bottom:6mm solid black}
          .page-number{text-align:center;font-size:7pt;margin-top:2mm;color:#333;font-family:Arial,sans-serif;border-top:0.2pt dotted #999;padding-top:1mm;flex-shrink:0}
          @media print{@page{size:A4;margin:0}body{width:210mm}.page{width:210mm;height:297mm;padding:8mm 12mm;page-break-after:always;break-after:page;overflow:hidden}.header,.student-section,.qr-area,.name-box,.id-box,.circle{border:0.5pt solid black!important;background:white!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}.instruction-text{border-left:2pt solid black!important;border-right:2pt solid black!important;background-color:#f9f9f9!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}.vertical-divider,.align{background:black!important;border-color:black!important;print-color-adjust:exact}.underline{border-bottom:0.5pt solid black!important}}
          @media screen{body{background:#e0e0e0;display:flex;flex-direction:column;align-items:center;padding:20px 0}.page{box-shadow:0 0 15px rgba(0,0,0,0.3);margin-bottom:25px;border:1px solid #ccc}}
        </style></head><body>${pagesHtml}</body></html>`);
      win.document.close();
      win.onload = () => win.print();
    } catch (err) {
      alert("Failed to load exam questions: " + err.message);
    }
  };

  if (exams.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-12 px-6">
        No exams match your search.
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {exams.map((exam, idx) => (
        <div
          key={exam.id}
          className="group flex items-center gap-4 px-5 py-4 cursor-pointer hover:bg-accent/40 transition-all duration-200"
          onClick={() => navigate(`/exams/${exam.id}`)}
        >
          {/* Index number */}
          <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center">
            <span className="text-sm font-bold text-primary">{idx + 1}</span>
          </div>

          {/* Main content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <h4 className="font-heading font-semibold text-sm truncate">{exam.title}</h4>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              {exam.subject && (
                <span className="flex items-center gap-1">
                  <Award className="h-3 w-3" />
                  {exam.subject}
                </span>
              )}
              {exam.date && (
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {exam.date}
                </span>
              )}
            </div>
          </div>

          {/* Stats badges */}
          <div className="hidden sm:flex items-center gap-2">
            <Badge variant="secondary" className="text-xs px-2.5 py-0.5 gap-1">
              <HelpCircle className="h-3 w-3" />
              {exam.statistics?.question_count || 0} Q
            </Badge>
            <Badge className="text-xs px-2.5 py-0.5 bg-primary/10 text-primary border-0">
              {exam.total_marks || 0} pts
            </Badge>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 cursor-pointer"
              title="Open & Print"
              onClick={(e) => handlePrint(e, exam)}
            >
              <Printer className="h-3.5 w-3.5 text-muted-foreground" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 cursor-pointer hover:text-destructive"
              title="Delete exam"
              onClick={(e) => handleDelete(e, exam.id)}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>

          {/* Chevron */}
          <ChevronRight className="h-4 w-4 text-muted-foreground/40 group-hover:text-primary group-hover:translate-x-0.5 transition-all duration-200 shrink-0" />
        </div>
      ))}
    </div>
  );
}
