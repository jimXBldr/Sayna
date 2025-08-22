from transformers import pipeline
print(pipeline("automatic-speech-recognition", "facebook/wav2vec2-large-xlsr-53"))