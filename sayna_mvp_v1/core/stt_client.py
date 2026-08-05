# sayna_mvp_v1/core/stt_client.py
from sayna_mvp_v1.contracts.transcription import TranscriptionResult, TranscriptMetadata
from sayna_mvp_v1.support.groq_errors_translator import translate_error
import tempfile
import os


class STTClient:
    def __init__(self, groq_client, model, response_format):
        """

        :param groq_client:
        :param model:
        :param response_format:
        """
        self._groq_client = groq_client
        self._model = model
        self._response_format = response_format

    def transcribe(self, audio):
        """

        :param audio:
        :return:
        """
        audio_file = self._create_audio_file(audio)
        try:
            response = self._groq_client.audio.transcriptions.create(file=audio_file,
                                                                     model=self._model,
                                                                     response_format=self._response_format)
            transcription_result = self._build_transcription_result(response)
            return transcription_result
        except Exception as e:
            print(type(e))
            print(e)
            failure_reason = translate_error(e)
            return TranscriptionResult(success=False, metadata=None, transcript=None, failure_reason=failure_reason)
        finally:
            audio_file.close()
            os.unlink(audio_file.name)

    def _create_audio_file(self, audio):
        """
        Creates the .wav audio file needed for groq
        :param audio: wav audio bytes.
        :return a file object containing the audio:
        """
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.write(audio)
        temp_file.close()
        return open(temp_file.name, 'rb')

    def _build_transcription_result(self, response) -> TranscriptionResult:
        """
        Translate the Groq response into a provider-independent TranscriptionResult
        :param response: Provider response
        :return: Transcription result
        """
        segment = response.segments[0]
        transcription_metadata = TranscriptMetadata(no_speech_probability=segment['no_speech_prob'],
                                                    average_log_probability=segment['avg_logprob'],
                                                    compression_ratio=segment['compression_ratio'])

        return TranscriptionResult(success=True, transcript=response.text, metadata=transcription_metadata,
                                   failure_reason=None)
