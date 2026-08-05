from io import BytesIO
from time import perf_counter
import threading
import wave

import numpy as np
import sounddevice as sd
from groq import Groq

from sayna_mvp_v1.support.config import load_config
from sayna_mvp_v1.core.stt_client import STTClient
from sayna_mvp_v1.core.llm_client import LLMClient
from core.intent_manager import IntentManager
from prompts.intent_prompt import IntentPrompt

SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio() -> bytes:
    """
    Records microphone audio until Enter is pressed.
    Returns WAV audio bytes.
    """

    print("Press Enter to start recording...")
    input()

    print("🎤 Recording...")
    print("Press Enter again to stop.\n")

    recorded_chunks = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recorded_chunks.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=callback,
    )

    stream.start()

    input()

    stream.stop()
    stream.close()

    audio = np.concatenate(recorded_chunks, axis=0)

    wav_buffer = BytesIO()

    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)  # int16 = 2 bytes
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio.tobytes())

    return wav_buffer.getvalue()


def main():

    # ---------------------------------------------------
    # Bootstrap
    # ---------------------------------------------------

    config = load_config()

    groq_client = Groq(
        api_key=config.groq_api_key
    )

    stt_client = STTClient(
        groq_client=groq_client,
        model=config.stt_model,
        response_format=config.stt_response_format,
    )

    llm_client = LLMClient(
        groq_client=groq_client,
        model=config.llm_model,
    )

    intent_manager = IntentManager(
        llm_client=llm_client,
        intent_prompt=IntentPrompt(),
    )

    # ---------------------------------------------------
    # Record Audio
    # ---------------------------------------------------

    audio = record_audio()

    # ---------------------------------------------------
    # Speech-To-Text
    # ---------------------------------------------------

    print("\nRunning Speech-To-Text...\n")

    stt_start = perf_counter()

    transcription = stt_client.transcribe(audio)

    stt_time = perf_counter() - stt_start

    print("=" * 50)
    print("STT RESULT")
    print("=" * 50)

    if not transcription.success:
        print(f"Failure : {transcription.failure_reason}")
        return

    print(f"Transcript : {transcription.transcript}")
    print(f"Latency    : {stt_time:.3f} seconds")

    # ---------------------------------------------------
    # Intent Detection
    # ---------------------------------------------------

    print("\nDetecting Intent...\n")

    intent_start = perf_counter()

    intent_result = intent_manager.detect_intent(
        transcription.transcript
    )

    intent_time = perf_counter() - intent_start

    print("=" * 50)
    print("INTENT RESULT")
    print("=" * 50)

    if not intent_result.success:
        print(f"Failure : {intent_result.failure_reason}")
        return

    print(f"Intent     : {intent_result.structured_request.intent}")
    print(f"Parameters : {intent_result.structured_request.parameters}")
    print(f"Latency    : {intent_time:.3f} seconds")

    # ---------------------------------------------------
    # Summary
    # ---------------------------------------------------

    total_time = stt_time + intent_time

    print("\n" + "=" * 50)
    print("PIPELINE SUMMARY")
    print("=" * 50)

    print(f"STT Time      : {stt_time:.3f} seconds")
    print(f"Intent Time   : {intent_time:.3f} seconds")
    print(f"Total Time    : {total_time:.3f} seconds")


if __name__ == "__main__":
    main()