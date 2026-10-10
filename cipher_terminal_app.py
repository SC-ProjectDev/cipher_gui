import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QLabel, QComboBox, 
    QPushButton, QSpinBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QClipboard

# -----------------------------------------------------------
# !!! IMPORTANT: Ensure 'cipher_backend.py' is in this directory !!!
# -----------------------------------------------------------
from cipher_backend import (
    CIPHERS, 
    frequency_analysis, 
    rot_brute_force, 
    reverse_text, 
    base64_encode, 
    base64_decode, 
    caesar_cipher, 
    rot47_core 
)

class CipherTerminalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Cipher Analysis Terminal v0.1")
        self.setGeometry(100, 100, 1000, 700)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.85)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._apply_stylesheet()
        self._setup_ui_layout()
        self._connect_signals() # New method for connections

    # ... (Stylesheet and _create_panel methods omitted for brevity) ... 
    # Use the previous code for these two methods.

    def _apply_stylesheet(self):
        """Applies the cyberpunk terminal-style QSS."""
        style = """
        QMainWindow, QWidget {
            background-color: black;
        }
        
        /* Neon green/cyan text and borders */
        QTextEdit, QLineEdit, QComboBox, QSpinBox, QLabel {
            background-color: #0d0d0d; /* Very dark gray for contrast */
            color: #00FFFF; /* Bright Cyan/Aqua for text */
            border: 1px solid #00AA77; /* Neon green border */
            padding: 5px;
            font-family: 'Courier New', monospace; 
            font-size: 14pt;
        }

        /* Buttons with a glow effect */
        QPushButton {
            background-color: #004444;
            color: #00FFFF;
            border: 2px solid #00AA77;
            padding: 10px;
            font-weight: bold;
            font-size: 12pt;
        }
        QPushButton:hover {
            background-color: #006666; /* Lighter background on hover */
            border-color: #00FF00; /* Brighter green on hover */
        }
        
        /* Checkable (Toggled) Button Style */
        QPushButton[flat="true"]:checked {
            background-color: #00AA77;
            color: black;
        }

        /* Headers and titles */
        QLabel#HeaderLabel {
            color: #00FF00; /* Primary neon green */
            font-size: 16pt;
            font-weight: bold;
            padding-bottom: 5px;
            border: none;
        }
        """
        self.setStyleSheet(style)

    def _create_panel(self, header: str, content_widget: QWidget) -> QWidget:
        """Helper to create a header and content within a structured panel."""
        panel_widget = QWidget()
        layout = QVBoxLayout(panel_widget)
        
        header_label = QLabel(header)
        header_label.setObjectName("HeaderLabel")
        
        layout.addWidget(header_label)
        layout.addWidget(content_widget)
        return panel_widget

    def _setup_ui_layout(self):
        # ... (Same layout setup as before) ...
        main_layout = QVBoxLayout(self.central_widget)
        
        # --- Top Half: Input/Output ---
        top_half = QHBoxLayout()
        
        self.input_text = QTextEdit()
        input_widget = self._create_panel("INPUT TEXT", self.input_text)
        top_half.addWidget(input_widget)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_widget = self._create_panel("DECRYPTED/ENCRYPTED OUTPUT", self.output_text)
        top_half.addWidget(output_widget)
        
        main_layout.addLayout(top_half, 4) 

        # --- Middle: Stats Panel ---
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Courier New", 10))
        stats_widget = self._create_panel("ANALYSIS & CRYPTOSCOPE", self.stats_text)
        main_layout.addWidget(stats_widget, 1)

        # --- Bottom: Controls & Cipher Select ---
        self.caesar_shift_input = QSpinBox()
        self.caesar_shift_input.setRange(1, 25)
        self.caesar_shift_input.setValue(3)
        self.caesar_shift_input.setToolTip("Caesar/ROT Shift")
        
        self.reverse_checkbox = QPushButton("Reverse") 
        self.reverse_checkbox.setCheckable(True)
        self.reverse_checkbox.setFlat(True) 
        self.reverse_checkbox.setProperty("flat", True) # Required for QSS toggling
        
        self.cipher_selector = QComboBox()
        self.cipher_selector.addItems([label for label, _, _, _ in CIPHERS.values()]) 
        self.cipher_selector.setCurrentText(CIPHERS["ROT47"][0]) # Set default to ROT-47
        
        self.process_button = QPushButton("RUN CIPHER➡️")
        self.bruteforce_button = QPushButton("BRUTE FORCE 💥")
        self.copy_button = QPushButton("COPY OUTPUT 📋")
        self.save_button = QPushButton("SAVE OUTPUT 💾")
        self.chain_button = QPushButton("CHAIN CIPHERS 🔗")

        control_layout = QGridLayout()
        
        control_layout.addWidget(QLabel("SELECT ALGO:"), 0, 0)
        control_layout.addWidget(self.cipher_selector, 0, 1)
        control_layout.addWidget(QLabel("SHIFT:"), 0, 2)
        control_layout.addWidget(self.caesar_shift_input, 0, 3)
        control_layout.addWidget(self.reverse_checkbox, 0, 4)

        control_layout.addWidget(self.process_button, 1, 0, 1, 2)
        control_layout.addWidget(self.bruteforce_button, 1, 2)
        control_layout.addWidget(self.copy_button, 1, 3)
        control_layout.addWidget(self.save_button, 1, 4)
        control_layout.addWidget(self.chain_button, 1, 5)

        main_layout.addLayout(control_layout, 1)

    def _connect_signals(self):
        """Connects all UI elements to their respective backend functions."""
        self.process_button.clicked.connect(self._run_cipher)
        self.copy_button.clicked.connect(self._copy_output)
        self.save_button.clicked.connect(self._save_output)
        self.bruteforce_button.clicked.connect(self._run_brute_force)
        
        # Real-time analysis update
        self.input_text.textChanged.connect(self._run_analysis)
        self.caesar_shift_input.valueChanged.connect(self._run_analysis) # Update stats if shift changes
        self.cipher_selector.currentTextChanged.connect(self._run_analysis) # Update stats if cipher changes

    ## ----------------------------------------------------
    ## CORE LOGIC IMPLEMENTATIONS
    ## ----------------------------------------------------

    def _run_cipher(self):
        """
        Executes the selected cipher on the input text and displays the result.
        Handles reversal logic before and after the cipher function.
        """
        input_text = self.input_text.toPlainText()
        if not input_text:
            self.output_text.setText("Input field is empty. Enter text to process.")
            return

        cipher_label = self.cipher_selector.currentText()
        
        # Find the function and metadata in the CIPHERS dictionary
        # We search by the display label since the combo box holds labels
        cipher_info = next(
            (info for info in CIPHERS.values() if info[0] == cipher_label), 
            None
        )

        if not cipher_info:
            self.output_text.setText("[ERROR: Cipher function not found.]")
            return

        _, cipher_fn, needs_shift, is_reversible = cipher_info
        
        # 1. Handle Reversal (Pre-processing)
        if self.reverse_checkbox.isChecked():
            # For decoding, if the 'reverse' box is checked, we reverse the input first
            input_text = reverse_text(input_text)

        # 2. Run Cipher Function
        try:
            if needs_shift:
                shift = self.caesar_shift_input.value()
                # Caesar/ROT functions are symmetric for encode/decode
                output = cipher_fn(input_text, shift)
            
            elif cipher_label in ["Base64 Encode", "Base64 Decode"]:
                # Handle Base64 separately since the CIPHERS table can't easily hold both
                if "Encode" in cipher_label:
                    output = base64_encode(input_text)
                else:
                    output = base64_decode(input_text)
            else:
                # Standard functions (ROT13, ROT47, Atbash)
                output = cipher_fn(input_text)
            
            # 3. Handle Reversal (Post-processing)
            # Since ROT/Atbash are self-inverting, if we run them once, it's decrypted/encoded.
            # No need to re-reverse here based on the original logic.

            self.output_text.setText(output)
        except Exception as e:
            self.output_text.setText(f"[ERROR DURING PROCESSING]\n{type(e).__name__}: {str(e)}")


    def _run_analysis(self):
        """Updates the analysis/stats panel in real-time."""
        input_text = self.input_text.toPlainText()
        output_str = ""
        
        # A. Frequency Analysis
        freqs = frequency_analysis(input_text)
        if freqs:
            top_freqs = [f"{char.upper()}: {freq:.2f}%" for char, freq in list(freqs.items())[:5]]
            output_str += "--- FREQUENCY ANALYSIS (Top 5) ---\n"
            output_str += " | ".join(top_freqs)
            output_str += "\n\n"
        else:
            output_str += "--- FREQUENCY ANALYSIS ---\n(Requires alphabetic characters)\n\n"

        # B. ROT47/ROT13 Suggestion (Simple guess based on characters)
        try:
            rot47_test = rot47_core(input_text)
            score = rot_brute_force(rot47_test) # Check the ROT47 result for English
            readability = sum(s[1] for s in score.values()) / len(score)
            
            output_str += "--- QUICK CRYPTO SUGGESTION ---\n"
            
            if all(c.isprintable() and ord(c) >= 33 and ord(c) <= 126 for c in input_text):
                 output_str += f"Potential ROT47/General Cipher. Avg Readability: {readability:.2f}\n"

        except:
             output_str += "Quick crypto analysis skipped (Non-standard input).\n"


        self.stats_text.setText(output_str)

    def _run_brute_force(self):
        """Runs the ROT brute force and displays the top 5 most likely decryptions."""
        input_text = self.input_text.toPlainText()
        if not input_text:
            QMessageBox.warning(self, "Brute Force Error", "Input field is empty. Cannot brute force.")
            return

        # Attempt to brute-force a standard Caesar/ROT cipher
        results = rot_brute_force(input_text)
        
        brute_output = "--- ROT/CAESAR BRUTE FORCE RESULTS ---\n"
        brute_output += "Shift | Score | Decrypted Text (Snippet)\n"
        brute_output += "--------------------------------------\n"
        
        # Display the top 5 highest-scoring results
        for i, (shift, (text, score)) in enumerate(results.items()):
            if i >= 5:
                break
            
            snippet = text.replace('\n', ' ')[:50].strip() + "..."
            brute_output += f"ROT{shift:02d} | {score:05.2f} | {snippet}\n"
        
        self.stats_text.setText(brute_output)
        self.output_text.setText(f"Top Brute Force Result (ROT{list(results.keys())[0]}):\n\n{list(results.values())[0][0]}")

    def _copy_output(self):
        """Copies the content of the Output Panel to the system clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        # Optional: Show a quick confirmation in the stats panel
        self.stats_text.setText("Output copied to clipboard.")

    def _save_output(self):
        """Opens a file dialog to save the output text."""
        options = QFileDialog.Option.DontUseNativeDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Cipher Output", 
            "", 
            "Text Files (*.txt);;All Files (*)", 
            options=options
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.output_text.toPlainText())
                self.stats_text.setText(f"Output successfully saved to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save file: {str(e)}")

# Main execution block
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CipherTerminalApp()
    window.show()
    sys.exit(app.exec())