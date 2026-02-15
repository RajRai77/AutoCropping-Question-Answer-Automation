Here is the **complete, professional `README.md` file**.

I have written it in a way that if you (or a recruiter) open this 6 months later, you will know exactly how to set it up again. It includes detailed **Step-by-Step guides for Poppler and Tesseract installation**.

### **Copy this content and save it as `README.md**`

```markdown
# 📄 JEE Question Paper Automation Tool

An automated Python script designed to extract, crop, and organize thousands of JEE (Joint Entrance Examination) questions and answers from PDF files. 

Instead of manually snipping images, this tool uses **Computer Vision (OpenCV)** and **OCR (Tesseract)** to detect question boundaries, remove headers/footers, and save high-quality images for mobile app databases.

---

## 🚀 Key Features

* **Smart Detection:** Automatically finds "Question No." and "Answer/Solution" keywords.
* **Intelligent Cropping:**
    * **Questions:** Extracts Question text + Options.
    * **Answers:** Extracts Answer Key + Detailed Solution + Diagrams.
* **Noise Removal:** "Brute-force" cropping removes advertisements, headers, and "Toll-Free" footers.
* **Auto-Sorting:** Organizes outputs into `Physics`, `Chemistry`, and `Maths` folders based on the source PDF.
* **Batch Processing:** Can process multiple Shift folders (e.g., "JEE 24 Feb Shift 1", "Shift 2") in one go.

---

## 🛠️ Prerequisites & Installation

To run this tool, you need to set up Python libraries and **two external system tools**.

### 1. Python Dependencies
Run the following command in your terminal to install the required libraries:

```bash
pip install pdf2image pytesseract opencv-python numpy

```

### 2. System Tools Setup (Crucial)

This script relies on **Poppler** (to read PDFs) and **Tesseract** (to read text). These must be installed on your Windows system.

#### A. Installing Poppler (For PDF conversion)

1. Download the latest binary from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/).
2. Extract the ZIP file to a location (e.g., `C:\Program Files\poppler`).
3. Open the extracted folder and locate the **`bin`** folder.
4. **Copy the path** (e.g., `C:\Program Files\poppler\Library\bin`).
5. **Add to Path:**
* Press `Windows Key`, type **"Edit the system environment variables"**, and hit Enter.
* Click **Environment Variables**.
* Under **System variables**, select **Path** and click **Edit**.
* Click **New** and paste the path to the `bin` folder.
* Click OK to save.



#### B. Installing Tesseract OCR (For Text Detection)

1. Download the installer from [UB-Mannheim Tesseract](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer. **Note the installation path** (usually `C:\Program Files\Tesseract-OCR` or `C:\Users\YourName\AppData\Local\Programs\Tesseract-OCR`).
3. **Add to Path:**
* Follow the same steps as above (Environment Variables -> Path -> Edit -> New).
* Paste the path to the folder where Tesseract is installed.
* Click OK to save.



*Verify installation:* Open a new terminal and type `tesseract -v`. If version info appears, you are ready!

---

## 📂 Project Structure

Your folder structure should look like this for the script to work:

```text
JEE_Automation_Project/
│
├── crop_questions.py        # The main script
├── README.md                # This documentation
│
├── JEE 24 Feb Shift 1/      # Input Folder 1
│   ├── Chemistry.pdf
│   ├── Maths.pdf
│   └── Physics.pdf
│
├── JEE 24 Feb Shift 2/      # Input Folder 2
│   └── ...
│
└── Final_Database_Images/   # (Auto-Generated Output)
    ├── Chemistry/
    │   ├── jee_24_feb_shift1_Question1.png
    │   └── jee_24_feb_shift1_Answer1.png
    ├── Physics/
    └── Maths/

```

---

## 🏃‍♂️ How to Run

1. Place your "Shift" folders (containing PDFs) in the same directory as the script.
2. Open your terminal in this directory.
3. Run the script:

```bash
python crop_questions.py

```

4. The script will print its progress:
* `--> Opening: Physics (JEE 24 Feb Shift 1)`
* `    Page 2: Found 4 potential blocks.`
* `      [SAVED] Answer for Q2`


5. Once finished, check the `Final_Database_Images` folder.

---

## 🧠 How the Logic Works

The script uses a **"Brute Force Anchor"** strategy:

1. **Page Cleaning:** It blindly crops the top 5% and bottom 15% of every page image. This guarantees that headers and footer advertisements (like "Toll Free") are removed before processing.
2. **Anchor Search:** It scans the remaining image for specific text patterns:
* **Question Start:** Digits at the start of a line (e.g., `1.`, `15`).
* **Answer Split:** Keywords like `Ans` or `Sol`.


3. **Dynamic Slicing:**
* When it finds a Question Number, it starts a crop.
* When it finds "Ans", it treats it as the start of the Solution block.
* It continues capturing the Solution until it detects the **Next Question Number**, ensuring the full explanation and diagrams are included.



---

## ⚠️ Troubleshooting

* **"Tesseract not found" error:**
* Ensure you added Tesseract to your System PATH.
* Alternatively, uncomment the line in the code:
`pytesseract.pytesseract.tesseract_cmd = r'C:\Path\To\tesseract.exe'`


* **"Poppler error" / "pdf2image error":**
* Ensure the `bin` folder of Poppler is in your System PATH.
* Restart your terminal/IDE after changing Environment Variables.



```

```