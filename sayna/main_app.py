import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtMultimedia import QSound
from sayna.backend.src.core.stt.whisper_adapter import WhisperSTTAdapter
from sayna.backend.src.core.nlu.intent_classifier import IntentClassifier
from sayna.backend.src.core.tts.espnet_adapter import CoquiTTSAdapter

class AudioProcessingThread(QThread):
    progress_updated = pyqtSignal(int)
    processing_finished = pyqtSignal(str, str)

    def __init__(self, audio_file, language):
        super().__init__()
        self.audio_file = audio_file
        self.language = language

    def run(self):
        try:
            # Initialize adapters
            stt = asyncio.run(WhisperSTTAdapter.get_instance())
            nlu = asyncio.run(IntentClassifier.get_instance())
            tts = asyncio.run(ESPnetTTSAdapter.get_instance())

            # Transcribe audio
            stt_result = asyncio.run(stt.transcribe(self.audio_file, detect_language=True))
            text = stt_result["text"]
            language = stt_result["language"]

            # Classify intent
            intent_result = asyncio.run(nlu.classify_intent(text, language=language))
            intent = intent_result["intent"]

            # Generate response
            response_text = self.generate_response(intent, text)
            response_audio = asyncio.run(tts.synthesize(response_text, language=language))

            # Save response audio to a file
            with open("response.wav", "wb") as f:
                f.write(response_audio)

            self.processing_finished.emit(text, response_text)
        except Exception as e:
            self.processing_finished.emit(str(e), "")

    def generate_response(self, intent, text):
        if intent == "send_email":
            return "I will send an email with your message."
        else:
            return "I'm sorry, I can't assist with that request."

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_file = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SAYNA Desktop App")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.label = QLabel("Upload an audio file to get started")
        layout.addWidget(self.label)

        self.upload_button = QPushButton("Upload Audio")
        self.upload_button.clicked.connect(self.upload_audio)
        layout.addWidget(self.upload_button)

        self.process_button = QPushButton("Process Audio")
        self.process_button.clicked.connect(self.process_audio)
        self.process_button.setEnabled(False)
        layout.addWidget(self.process_button)

        self.play_button = QPushButton("Play Response")
        self.play_button.clicked.connect(self.play_response)
        self.play_button.setEnabled(False)
        layout.addWidget(self.play_button)

        self.text_display = QLabel("")
        self.text_display.setWordWrap(True)
        layout.addWidget(self.text_display)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        central_widget.setLayout(layout)

    def upload_audio(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "Audio Files (*.wav *.mp3)", options=options)
        if file_name:
            self.audio_file = file_name
            self.label.setText(f"Audio file uploaded: {file_name}")
            self.process_button.setEnabled(True)

    def process_audio(self):
        if not self.audio_file:
            self.label.setText("Please upload an audio file first.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.thread = AudioProcessingThread(self.audio_file, "en")
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.processing_finished.connect(self.processing_done)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def processing_done(self, text, response_text):
        self.progress_bar.setVisible(False)
        if text:
            self.text_display.setText(f"Recognized Text: {text}\nResponse: {response_text}")
            self.play_button.setEnabled(True)
        else:
            self.text_display.setText(f"Error: {text}")

    def play_response(self):
        QSound.play("response.wav")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())