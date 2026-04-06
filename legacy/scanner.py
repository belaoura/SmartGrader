"""
Smart Grader Scanner - Bubble Detection & Mapping
Detects triangles, links them, finds bubbles, and maps them to questions.
Uses exact choices count per question from database.
"""

import cv2
import numpy as np
import os
import database
import fitz

INPUT_FILE = "QCM Answer Sheet1.pdf"
OUTPUT_FILE = "scanned_result.jpg"
PDF_DPI = 300
FILL_THRESHOLD = 50


def load_image(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        print(f"Converting PDF to image...")
        doc = fitz.open(file_path)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        doc.close()
        return img, 1
    else:
        img = cv2.imread(file_path)
        return img, 1


def detect_triangles_and_lines(img):
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners = [gray[0, 0], gray[0, width-1], gray[height-1, 0], gray[height-1, width-1]]
    bg_color = np.mean(corners)
    
    if bg_color < 127:
        gray = cv2.bitwise_not(gray)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    found_triangles = []

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)
        if len(approx) == 3:
            area = cv2.contourArea(cnt)
            if area > 400:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    found_triangles.append({"center": (cX, cY), "area": area, "contour": approx})

    found_triangles.sort(key=lambda t: t["area"], reverse=True)
    best_4 = found_triangles[:4]

    if len(best_4) != 4:
        return None, None, None

    centers = [t["center"] for t in best_4]
    
    for t in best_4:
        cv2.drawContours(img, [t["contour"]], 0, (0, 255, 0), 3)

    linked = set()
    pairs = []
    
    for i, t1 in enumerate(centers):
        if i in linked:
            continue
        best_dist = float('inf')
        best_j = None
        for j, t2 in enumerate(centers):
            if j <= i or j in linked:
                continue
            dist = np.sqrt((t1[0] - t2[0])**2 + (t1[1] - t2[1])**2)
            if dist < best_dist:
                best_dist = dist
                best_j = j
        if best_j is not None:
            pairs.append((i, best_j))
            linked.add(i)
            linked.add(best_j)

    line_ys = []
    for i, j in pairs:
        y = (centers[i][1] + centers[j][1]) // 2
        line_ys.append(y)
        cv2.line(img, (0, y), (img.shape[1], y), (255, 0, 0), 5)

    line_ys.sort()
    return line_ys[0], line_ys[-1], best_4


def detect_question_lines(img, top_y, bottom_y):
    roi = img[top_y:bottom_y, :]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    kernel_length = roi.shape[1] // 10
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    contours, _ = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    line_positions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < 15 and w >= kernel_length:
            actual_y = top_y + y + h // 2
            line_positions.append((x, actual_y, w, h))
    
    line_positions.sort(key=lambda l: l[1])
    
    filtered = []
    min_gap = 15
    for line in line_positions:
        is_dup = False
        for f in filtered:
            if abs(line[1] - f[1]) < min_gap:
                is_dup = True
                break
        if not is_dup:
            filtered.append(line)
    
    print(f"Detected {len(line_positions)} lines, {len(filtered)} after filtering")
    return filtered


def detect_bubbles_in_section(img, top_y, bottom_y):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 4)
    kernel = np.ones((2, 2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    mid_x = img.shape[1] // 2
    img_width = img.shape[1]
    bubbles = []
    
    left_col_min = int(img_width * 0.08)
    left_col_max = int(img_width * 0.25)
    right_col_min = int(img_width * 0.45)
    right_col_max = int(img_width * 0.75)
    
    margin = 40
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 60 or area > 600:
            continue
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < 0.65:
            continue
        x, y, cw, ch = cv2.boundingRect(cnt)
        aspect = cw / ch if ch > 0 else 0
        if aspect < 0.6 or aspect > 1.5:
            continue
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            r = int(np.sqrt(area / np.pi))
            if r < 6 or r > 25:
                continue
            if top_y + margin < cy < bottom_y - margin:
                col = None
                if left_col_min <= cx <= left_col_max:
                    col = 'L'
                elif right_col_min <= cx <= right_col_max:
                    col = 'R'
                
                if col:
                    bubbles.append({'x': cx, 'y': cy, 'r': r, 'area': area, 'col': col})
    
    final = []
    for b in bubbles:
        is_dup = False
        for f in final:
            dist = np.sqrt((b['x'] - f['x'])**2 + (b['y'] - f['y'])**2)
            if dist < 10:
                is_dup = True
                break
        if not is_dup:
            final.append(b)
    
    if len(final) >= 4:
        left_bubbles = [b for b in final if b['col'] == 'L']
        right_bubbles = [b for b in final if b['col'] == 'R']
        
        avg_left_x = sum(b['x'] for b in left_bubbles) / len(left_bubbles) if left_bubbles else 0
        avg_right_x = sum(b['x'] for b in right_bubbles) / len(right_bubbles) if right_bubbles else 0
        
        max_deviation = 50
        
        verified = []
        for b in final:
            if b['col'] == 'L':
                if abs(b['x'] - avg_left_x) <= max_deviation:
                    verified.append(b)
            else:
                if abs(b['x'] - avg_right_x) <= max_deviation:
                    verified.append(b)
        
        removed = len(final) - len(verified)
        if removed > 0:
            print(f"  Removed {removed} outliers (letters like 'o')")
        final = verified
    
    if len(final) < 80:
        gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh2 = cv2.threshold(gray2, 127, 255, cv2.THRESH_BINARY_INV)
        contours2, _ = cv2.findContours(thresh2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours2:
            area = cv2.contourArea(cnt)
            if area < 60 or area > 600:
                continue
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.65:
                continue
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                r = int(np.sqrt(area / np.pi))
                if r < 6 or r > 25:
                    continue
                if top_y + margin < cy < bottom_y - margin:
                    col = None
                    if left_col_min <= cx <= left_col_max:
                        col = 'L'
                    elif right_col_min <= cx <= right_col_max:
                        col = 'R'
                    
                    if col:
                        new_b = {'x': cx, 'y': cy, 'r': r, 'area': area, 'col': col}
                        is_dup = False
                        for f in final:
                            dist = np.sqrt((cx - f['x'])**2 + (cy - f['y'])**2)
                            if dist < 10:
                                is_dup = True
                                break
                        if not is_dup:
                            final.append(new_b)
    
    print(f"  Detected {len(final)} bubbles")
    return final


def check_if_filled(img, bubble):
    x, y, r = bubble['x'], bubble['y'], bubble['r']
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dark_pixels = cv2.countNonZero(cv2.bitwise_not(gray) & mask)
    total_pixels = cv2.countNonZero(mask)
    if total_pixels == 0:
        return False, 0
    fill_percentage = (dark_pixels / total_pixels) * 100
    return fill_percentage >= FILL_THRESHOLD, fill_percentage


def get_exam_questions(exam_id):
    questions = database.get_questions_by_exam(exam_id)
    exam_info = []
    for q in questions:
        q_id, q_text, choices_num, q_marks = q
        exam_info.append({'question_id': q_id, 'text': q_text, 'choices_count': choices_num, 'marks': q_marks})
    return exam_info


def get_exam_info(exam_id):
    exam = database.get_exam_details(exam_id)
    if not exam:
        return None
    return {'id': exam[0], 'title': exam[1], 'subject': exam[2], 'date': exam[3], 'total_marks': exam[4]}


def map_bubbles_to_questions(bubbles, exam_questions, question_lines, img):
    """Map bubbles to questions using database choices count - follows exact numerical order"""
    left_col = [b for b in bubbles if b['col'] == 'L']
    right_col = [b for b in bubbles if b['col'] == 'R']
    left_col.sort(key=lambda c: c['y'])
    right_col.sort(key=lambda c: c['y'])
    
    exam_questions_sorted = sorted(exam_questions, key=lambda q: q['question_id'])
    
    left_bubble_count = len(left_col)
    
    left_questions = []
    bubble_idx = 0
    for q in exam_questions_sorted:
        if bubble_idx + q['choices_count'] <= left_bubble_count:
            left_questions.append(q)
            bubble_idx += q['choices_count']
        else:
            break
    
    right_questions = [q for q in exam_questions_sorted if q not in left_questions]
    
    choice_labels = ['a', 'b', 'c', 'd', 'e', 'f']
    
    def assign_to_column(col_bubbles, questions_list, col_type):
        result = {}
        bubble_idx = 0
        questions_mapped = []
        print(f"\n{col_type} column: {len(col_bubbles)} bubbles")
        
        for q in questions_list:
            choices_count = q['choices_count']
            q_id = q['question_id']
            
            bubbles_for_q = []
            while bubble_idx < len(col_bubbles) and len(bubbles_for_q) < choices_count:
                bubbles_for_q.append(col_bubbles[bubble_idx])
                bubble_idx += 1
            
            if len(bubbles_for_q) < choices_count:
                print(f"  Q{q_id} ({choices_count} choices): {len(bubbles_for_q)} circles - BUBBLES ENDED")
                break
            
            print(f"  Q{q_id} ({choices_count} choices): {len(bubbles_for_q)} circles")
            questions_mapped.append(q_id)
            
            for j, bubble in enumerate(bubbles_for_q):
                if j < len(choice_labels):
                    bubble['question'] = q_id
                    bubble['choice'] = choice_labels[j]
                    bubble['label'] = f"Q{q_id}{choice_labels[j]}"
                    result[f"Q{q_id}{choice_labels[j]}"] = bubble
        
        return result, questions_mapped
    
    left_result, left_mapped = assign_to_column(left_col, left_questions, "LEFT")
    right_result, right_mapped = assign_to_column(right_col, right_questions, "RIGHT")
    
    left_result.update(right_result)
    all_mapped = left_mapped + right_mapped
    
    return left_result, left_col, right_col, all_mapped


def detect_and_map_bubbles(image_path, exam_id, output_path=None):
    img, _ = load_image(image_path)
    if img is None:
        print(f"Could not load: {image_path}")
        return None, None
    
    print(f"\nLoaded: {image_path} ({img.shape[1]}x{img.shape[0]})")
    
    exam_info = get_exam_info(exam_id)
    if not exam_info:
        print(f"Exam {exam_id} not found!")
        return None, None
    
    exam_questions = get_exam_questions(exam_id)
    
    print(f"\n{'='*50}")
    print(f"EXAM INFO FROM DATABASE")
    print(f"{'='*50}")
    print(f"ID: {exam_info['id']}")
    print(f"Title: {exam_info['title']}")
    print(f"Total Questions: {len(exam_questions)}")
    print(f"{'='*50}")
    
    top_y, bottom_y, triangles = detect_triangles_and_lines(img)
    
    if top_y is None:
        print("Warning: Could not detect 4 triangles!")
        return None, None
    
    print(f"\nSection: y={top_y} to y={bottom_y}")
    
    bubbles = detect_bubbles_in_section(img, top_y, bottom_y)
    mapped_bubbles, left_col, right_col, detected_questions = map_bubbles_to_questions(bubbles, exam_questions, None, img)
    
    print(f"\n{'='*50}")
    print(f"BUBBLE MAPPING")
    print(f"{'='*50}")
    for label in sorted(mapped_bubbles.keys()):
        bubble = mapped_bubbles[label]
        print(f"  {label}: ({bubble['x']}, {bubble['y']})")
    
    total_questions = len(exam_questions)
    detected_set = set(detected_questions)
    if len(detected_set) < total_questions:
        remaining = total_questions - len(detected_set)
        print(f"\n{'='*50}")
        print(f"*** MORE SHEETS DETECTED ***")
        print(f"{'='*50}")
        print(f"Detected questions: {', '.join(['Q'+str(q) for q in sorted(detected_questions)])} ({len(detected_set)} questions)")
        print(f"Remaining: {remaining} questions")
        print(f"Total in exam: {total_questions}")
        print(f"*** Please scan remaining sheets to complete grading! ***")
        print(f"{'='*50}")
    else:
        print(f"\n*** All questions detected on this sheet ({total_questions}/{total_questions}) ***")
    
    if output_path:
        result_img = img.copy()
        cv2.line(result_img, (0, top_y), (img.shape[1], top_y), (255, 0, 0), 4)
        cv2.line(result_img, (0, bottom_y), (img.shape[1], bottom_y), (255, 0, 0), 4)
        
        colors = [(0, 255, 0), (0, 255, 255), (255, 0, 255), (0, 128, 255), (128, 0, 255), (255, 255, 0)]
        
        for label, bubble in mapped_bubbles.items():
            q_num = bubble.get('question', 0)
            color = colors[q_num % len(colors)]
            cv2.circle(result_img, (bubble['x'], bubble['y']), bubble['r'], color, 3)
            cv2.circle(result_img, (bubble['x'], bubble['y']), 3, (0, 0, 0), -1)
            cv2.putText(result_img, label, (bubble['x'] + 15, bubble['y'] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imwrite(output_path, result_img)
        print(f"\nSaved: {output_path}")
    
    return mapped_bubbles, exam_questions


def grade_sheet(mapped_bubbles, exam_questions, img=None):
    results = []
    total_marks = 0
    obtained_marks = 0
    answered_count = 0
    
    detected_questions = set()
    for bubble in mapped_bubbles.values():
        if 'question' in bubble:
            detected_questions.add(bubble['question'])
    
    questions_to_grade = [q for q in exam_questions if q['question_id'] in detected_questions]
    questions_to_skip = [q for q in exam_questions if q['question_id'] not in detected_questions]
    
    print(f"\n{'='*65}")
    print(f"GRADING RESULTS (Questions on this sheet)")
    print(f"{'='*65}")
    print(f"{'Q#':<6} {'Fill%':<8} {'Detected':<12} {'Correct':<12} {'Result':<10}")
    print(f"{'-'*65}")
    
    for q in questions_to_grade:
        q_id = q['question_id']
        total_marks += q['marks']
        
        choices = database.get_choices_by_question(q_id)
        correct_choice = None
        for c in choices:
            if c[3] == 1:
                correct_choice = c[1].lower()
                break
        
        choice_labels = ['a', 'b', 'c', 'd', 'e', 'f']
        best_fill = 0
        best_choice = None
        
        for i, label_char in enumerate(choice_labels):
            label = f"Q{q_id}{label_char}"
            if label in mapped_bubbles and img is not None:
                bubble = mapped_bubbles[label]
                is_filled, fill_percentage = check_if_filled(img, bubble)
                if fill_percentage > best_fill:
                    best_fill = fill_percentage
                    best_choice = label_char
        
        detected_choice = best_choice if best_fill >= FILL_THRESHOLD else None
        if detected_choice:
            answered_count += 1
        
        is_correct = (detected_choice == correct_choice)
        if is_correct:
            obtained_marks += q['marks']
        
        result_icon = "[+]" if is_correct else "[-]"
        print(f"Q{q_id:<5} {best_fill:>5.1f}%  {detected_choice if detected_choice else '-':<12} {correct_choice if correct_choice else '-':<12} {result_icon}")
        
        results.append({'question_id': q_id, 'detected': detected_choice, 'correct': correct_choice, 'is_correct': is_correct, 'marks': q['marks']})
    
    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
    
    print(f"{'='*65}")
    print(f"TOTAL: {obtained_marks}/{total_marks} ({percentage:.1f}%)")
    print(f"Answered: {answered_count}/{len(questions_to_grade)}")
    
    if questions_to_skip:
        print(f"\n*** Skipped (on other sheets): {len(questions_to_skip)} questions ***")
        print(f"    Missing questions: {', '.join(['Q'+str(q['question_id']) for q in questions_to_skip])}")
    print(f"{'='*65}")
    
    return {'results': results, 'total_marks': total_marks, 'obtained_marks': obtained_marks, 'percentage': percentage, 'detected_questions': detected_questions}


if __name__ == "__main__":
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("="*60)
    print("SMART GRADER SCANNER")
    print("="*60)
    
    if len(sys.argv) > 1:
        exam_id = int(sys.argv[1])
    else:
        exams = database.get_exams()
        print("\nAVAILABLE EXAMS:")
        for e in exams:
            print(f"  [{e[0]}] {e[1]}")
        exam_id = int(input("\nEnter exam ID: "))
    
    input_file = sys.argv[2] if len(sys.argv) > 2 else INPUT_FILE
    input_path = os.path.join(script_dir, input_file)
    output_path = os.path.join(script_dir, OUTPUT_FILE)
    
    if os.path.exists(input_path):
        mapped_bubbles, exam_questions = detect_and_map_bubbles(input_path, exam_id, output_path)
        if mapped_bubbles and exam_questions:
            img, _ = load_image(input_path)
            grade_result = grade_sheet(mapped_bubbles, exam_questions, img)
    else:
        print(f"File not found: {input_file}")
