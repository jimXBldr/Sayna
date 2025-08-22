from TTS.api import TTS

# Pick a pretrained model (this will download it once)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

# Generate speech
tts.tts_to_file(text="Hello, this is a test of Coqui running offline!",
                file_path="test.wav")
print("✅ Speech saved to test.wav")
