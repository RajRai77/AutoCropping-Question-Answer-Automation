import os
import cv2
import pytesseract
import numpy as np
import re
from pdf2image import convert_from_path

# ================= CONFIGURATION =================
ROOT_DIR = "."  
OUTPUT_DIR = "Final_Database_Images"

# ADJUST THIS IF NEEDED:
# If you are on Windows and Tesseract is not in Path, uncomment line below:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Users\kavir\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
# =================================================

def create_folders():
    subjects = ["Chemistry", "Physics", "Maths"]
    for sub in subjects:
        path = os.path.join(OUTPUT_DIR, sub)
        if not os.path.exists(path):
            os.makedirs(path)

def clean_filename(text):
    return text.lower().replace(" ", "_")

def process_pdf(pdf_path, subject, shift_name):
    print(f"\n--> Opening: {subject} ({shift_name})")
    
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        print(f"    Loaded {len(pages)} pages.")
    except Exception as e:
        print(f"    ERROR reading PDF: {e}")
        return

    last_q_num = "0"

    for page_num, page_pil in enumerate(pages):
        # Skip Page 1 (Usually Title Page)
        if page_num == 0: 
            continue

        img = np.array(page_pil)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        h, w, _ = img.shape
        
        # --- 1. THE BRUTE FORCE CROP (Fixes Footer/Header) ---
        # We blindly remove Top 5% and Bottom 15%. 
        # This deletes the "Toll Free" footer instantly.
        top_cut = int(h * 0.05)
        bottom_cut = int(h * 0.85) # Cut off bottom 15%
        
        # Working Area
        roi = img[top_cut:bottom_cut, 0:w]
        
        # --- 2. RELAXED OCR SCAN ---
        # psm 6 = Assume uniform block of text
        data = pytesseract.image_to_data(roi, output_type=pytesseract.Output.DICT, config='--psm 6')
        
        anchors = []
        
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if not text: continue
            
            x = data['left'][i]
            y = data['top'][i] + top_cut # Adjust Y because we cropped top
            
            # --- DEBUG: Uncomment if you want to see what text it reads ---
            # if page_num == 1: print(f"Text: {text} | x: {x}")

            # A. Detect Question Start
            # Logic: Starts with digit, followed by dot OR paren, OR just a digit 
            # AND is on the Left side (x < 300 - Widened from 150)
            if x < 300:
                # Match "1." or "1)" or just "1" if it's isolated
                if re.match(r'^\d+[\.\)]?$', text):
                    anchors.append({'type': 'Q_START', 'val': text, 'y': y})
            
            # B. Detect Answer Split
            if "Ans" in text or "Ans." in text:
                anchors.append({'type': 'SPLIT_POINT', 'val': 'Ans', 'y': y})
            elif "Sol" in text or "Sol." in text:
                anchors.append({'type': 'SPLIT_POINT', 'val': 'Sol', 'y': y})

        # Sort anchors
        anchors.sort(key=lambda k: k['y'])
        
        # Deduplicate Anchors (Sometimes OCR reads "1" then "." as two items)
        # We only keep unique Y positions (roughly)
        unique_anchors = []
        if anchors:
            unique_anchors.append(anchors[0])
            for k in range(1, len(anchors)):
                # If new anchor is far enough from previous (>20px), keep it
                if anchors[k]['y'] - unique_anchors[-1]['y'] > 20:
                    unique_anchors.append(anchors[k])
        anchors = unique_anchors

        print(f"    Page {page_num+1}: Found {len(anchors)} potential blocks.")

        # --- 3. CROPPER ---
        for i, anchor in enumerate(anchors):
            start_y = max(top_cut, anchor['y'] - 10)
            
            # End Y is either next anchor or the hard bottom cut
            if i + 1 < len(anchors):
                end_y = anchors[i+1]['y'] - 15
            else:
                end_y = bottom_cut
            
            # Validation
            if end_y - start_y < 50: continue

            # Extract
            crop_img = img[start_y:end_y, 0:w]
            clean_shift = clean_filename(shift_name)

            if anchor['type'] == 'Q_START':
                # Extract number
                q_num = re.sub(r'\D', '', anchor['val'])
                # Fallback if OCR read garbage
                if not q_num: q_num = "Unknown"
                else: last_q_num = q_num
                
                fname = f"{clean_shift}_Question{q_num}.png"
                save_path = os.path.join(OUTPUT_DIR, subject, fname)
                
                if not os.path.exists(save_path):
                    cv2.imwrite(save_path, crop_img)
                    # print(f"      Saved Q{q_num}") # Reduced noise

            elif anchor['type'] == 'SPLIT_POINT':
                # It's an Answer. 
                # We save it, but we need to ensure we don't cut it short if "Sol" follows "Ans"
                # The sorting handles order, but we might have separate crops for "Ans" and "Sol".
                # To fix the "Split" issue:
                # We only save if the block is BIG enough, or if it contains the solution text.
                
                # Check if this is "Ans" (Start of answer)
                if "Ans" in anchor['val']:
                    # Look ahead! Extend crop to the NEXT QUESTION
                    real_end_y = bottom_cut
                    for k in range(i+1, len(anchors)):
                        if anchors[k]['type'] == 'Q_START':
                            real_end_y = anchors[k]['y'] - 15
                            break
                    
                    # Re-Crop full Answer + Solution
                    full_ans_img = img[start_y:real_end_y, 0:w]
                    
                    if last_q_num != "0":
                        fname = f"{clean_shift}_Answer{last_q_num}.png"
                        save_path = os.path.join(OUTPUT_DIR, subject, fname)
                        if not os.path.exists(save_path):
                            cv2.imwrite(save_path, full_ans_img)
                            print(f"      [SAVED] Answer for Q{last_q_num}")

def main():
    print("=== STARTING BRUTE FORCE CROPPER ===")
    create_folders()
    
    for root, dirs, files in os.walk(ROOT_DIR):
        folder_name = os.path.basename(root)
        if "Shift" in folder_name:
            for file in files:
                if file.lower().endswith('.pdf'):
                    sub = None
                    if "chemistry" in file.lower(): sub = "Chemistry"
                    elif "physics" in file.lower(): sub = "Physics"
                    elif "math" in file.lower(): sub = "Maths"
                    
                    if sub:
                        process_pdf(os.path.join(root, file), sub, folder_name)
    
    print("\n=== DONE. CHECK FOLDERS. ===")

if __name__ == "__main__":
    main()