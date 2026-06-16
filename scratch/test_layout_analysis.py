import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

def analyze_page_layout(page_num):
    page = doc[page_num]
    words = page.get_text("words") # list of tuples: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
    
    # 1. Find the table header y-coordinate
    # We look for "Evidencia" and "Criterios"
    y_header = None
    for w in words:
        if w[4].lower() == "evidencia":
            # Check if there's "criterios" nearby
            y_header = w[3] # y1 of the word "evidencia"
            break
            
    if y_header is None:
        # Fallback if we don't find it
        y_header = 150.0
        
    print(f"Page {page_num+1}: y_header = {y_header:.1f}")
    
    # 2. Filter words below header and above footer (y = 550)
    table_words = [w for w in words if w[1] > y_header and w[3] < 550]
    
    # 3. Separate into Left (Evidence) and Right (Criteria) columns
    # We use x0 = 185 as the split coordinate
    left_words = [w for w in table_words if w[0] < 185]
    right_words = [w for w in table_words if w[0] >= 185 and w[2] < 390]
    
    # Helper to group words into lines and then paragraphs
    def words_to_paragraphs(column_words, column_name):
        if not column_words:
            return []
            
        # Group words into lines based on y0/y1 overlap
        lines = []
        column_words.sort(key=lambda w: (w[1], w[0]))
        
        current_line = []
        for w in column_words:
            if not current_line:
                current_line.append(w)
            else:
                # Check if this word is on the same line (y0 difference is small)
                # We can check if y0 of the word is less than y1 of the last word in line
                last_w = current_line[-1]
                # If they overlap vertically, or the difference between their y-centers is small
                last_center_y = (last_w[1] + last_w[3]) / 2
                curr_center_y = (w[1] + w[3]) / 2
                if abs(last_center_y - curr_center_y) < 4:
                    current_line.append(w)
                else:
                    lines.append(current_line)
                    current_line = [w]
        if current_line:
            lines.append(current_line)
            
        # Sort each line from left to right and join
        text_lines = []
        for line in lines:
            line.sort(key=lambda w: w[0])
            line_text = " ".join([w[4] for w in line])
            # get bounding box of the line
            lx0 = min(w[0] for w in line)
            ly0 = min(w[1] for w in line)
            lx1 = max(w[2] for w in line)
            ly1 = max(w[3] for w in line)
            text_lines.append({"text": line_text, "bbox": (lx0, ly0, lx1, ly1)})
            
        # Group lines into paragraphs based on vertical gap
        paragraphs = []
        current_para = []
        for idx, line in enumerate(text_lines):
            if not current_para:
                current_para.append(line)
            else:
                # Check vertical gap between this line and the previous one
                prev_line = current_para[-1]
                gap = line["bbox"][1] - prev_line["bbox"][3]
                # If gap is small (e.g. less than 8 points), it's the same paragraph
                if gap < 8:
                    current_para.append(line)
                else:
                    paragraphs.append(current_para)
                    current_para = [line]
        if current_para:
            paragraphs.append(current_para)
            
        # Format paragraphs
        formatted_paras = []
        for para in paragraphs:
            para_text = " ".join([l["text"] for l in para])
            px0 = min(l["bbox"][0] for l in para)
            py0 = min(l["bbox"][1] for l in para)
            px1 = max(l["bbox"][2] for l in para)
            py1 = max(l["bbox"][3] for l in para)
            formatted_paras.append({"text": para_text, "bbox": (px0, py0, px1, py1)})
            
        return formatted_paras

    left_paras = words_to_paragraphs(left_words, "Left")
    right_paras = words_to_paragraphs(right_words, "Right")
    
    print(f"\n--- LEFT COLUMN (EVIDENCES) ({len(left_paras)} items) ---")
    for idx, p in enumerate(left_paras):
        print(f"Ev {idx+1}: bbox=({p['bbox'][0]:.1f}, {p['bbox'][1]:.1f}, {p['bbox'][2]:.1f}, {p['bbox'][3]:.1f}) | {p['text']}")
        
    print(f"\n--- RIGHT COLUMN (CRITERIA) ({len(right_paras)} items) ---")
    for idx, p in enumerate(right_paras):
        print(f"Cr {idx+1}: bbox=({p['bbox'][0]:.1f}, {p['bbox'][1]:.1f}, {p['bbox'][2]:.1f}, {p['bbox'][3]:.1f}) | {p['text']}")

print("TESTING PAGE 20:")
analyze_page_layout(19)

print("\n" + "="*80 + "\n")

print("TESTING PAGE 32:")
analyze_page_layout(31)
