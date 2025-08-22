"""
Audio processing utilities for SAYNA Voice OS.
Handles audio file operations, format conversions, and validations.
"""

import io
import logging
from pathlib import Path
from typing import Optional, Tuple, Union  # just for type hints ide friendly
import tempfile  # to create temporary files in disk

import numpy as np
import soundfile as sf  # to read or write audio files
from pydub import AudioSegment  # for audio manipulation using ffmpeg
from pydub.exceptions import CouldntDecodeError

logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {
    'wav': {'extension': 'wav', 'mime_type': 'audio/wav'},
    'mp3': {'extension': 'mp3', 'mime_type': 'audio/mpeg'},
    'ogg': {'extension': 'ogg', 'mime_type': 'audio/ogg'},
    'flac': {'extension': 'flac', 'mime_type': 'audio/flac'}
}

# Audio parameters
DEFAULT_SAMPLE_RATE = 16000  # 16kHz sample rate
DEFAULT_CHANNELS = 1  # Mono audio
DEFAULT_BIT_DEPTH = 16  # 16-bit audio


def validate_audio_file(audio_data: bytes) -> bool:
    """
    Validate audio file format and basic parameters.

    Args:
        audio_data: Audio data in bytes

    Returns:
        bool: True if audio is valid, False otherwise
    """
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp_file:
            tmp_file.write(audio_data)
            tmp_file.flush()

            # Try reading with soundfile
            with sf.SoundFile(tmp_file.name) as sound_file:
                if sound_file.channels not in (1, 2):
                    logger.warning(f"Unsupported channel count: {sound_file.channels}")
                    return False

                if sound_file.samplerate < 8000 or sound_file.samplerate > 48000:
                    logger.warning(f"Unsupported sample rate: {sound_file.samplerate}")
                    return False

                return True
    except Exception as e:
        logger.warning(f"Audio validation failed: {str(e)}")
        return False


def preprocess_audio(
        audio_data: Union[bytes, np.ndarray, str],
        target_sample_rate: int = DEFAULT_SAMPLE_RATE,
        target_channels: int = DEFAULT_CHANNELS
) -> np.ndarray:
    """
    Preprocess audio to standard format for processing.

    Args:
        audio_data: Input audio as bytes, file path, or numpy array
        target_sample_rate: Target sample rate in Hz
        target_channels: Target number of channels

    Returns:
        np.ndarray: Processed audio as mono float32 numpy array
    """
    try:
        # Convert input to numpy array if needed
        if isinstance(audio_data, bytes):
            audio_array = _bytes_to_numpy(audio_data)
        elif isinstance(audio_data, str):
            audio_array, _ = sf.read(audio_data)
        elif isinstance(audio_data, np.ndarray):
            audio_array = audio_data
        else:
            raise ValueError(f"Unsupported audio type: {type(audio_data)}")

        # Convert to mono if needed
        if len(audio_array.shape) > 1 and audio_array.shape[1] > 1:
            audio_array = np.mean(audio_array, axis=1)

        # Normalize to float32 range [-1, 1]
        if audio_array.dtype != np.float32:
            if np.issubdtype(audio_array.dtype, np.integer):
                max_val = np.iinfo(audio_array.dtype).max
                audio_array = audio_array.astype(np.float32) / max_val
            else:
                audio_array = audio_array.astype(np.float32)

        return audio_array

    except Exception as e:
        logger.error(f"Audio preprocessing failed: {str(e)}")
        raise ValueError(f"Audio preprocessing failed: {str(e)}")


def _bytes_to_numpy(audio_bytes: bytes) -> np.ndarray:
    """
    Convert audio bytes to numpy array.

    Args:
        audio_bytes: Audio data in bytes

    Returns:
        np.ndarray: Audio as numpy array
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        raw_samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        if audio.channels > 1:
            raw_samples = raw_samples.reshape((-1, audio.channels)).mean(axis=1)
        # Normalize
        max_val = 1 << (8 * audio.sample_width * 8)
        return raw_samples / max_val
    except Exception as e:
        logger.error(f"Failed to decode audio bytes")
        raise ValueError(f"Unsupported or corrupted audio data:  {str(e)}")


def save_audio_to_bytes(
        audio_array: np.ndarray,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        format: str = 'wav',
        bit_depth: int = DEFAULT_BIT_DEPTH
) -> bytes:
    """
    Save numpy audio array to bytes in specified format.

    Args:
        audio_array: Input audio array
        sample_rate: Sample rate in Hz
        format: Output format ('wav', 'mp3', etc.)
        bit_depth: Bit depth (16 or 32)

    Returns:
        bytes: Audio data in bytes
    """
    if format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {format}. Supported: {list(SUPPORTED_FORMATS.keys())}")

    try:
        # Convert array to correct format
        if bit_depth == 16:
            audio_array = (audio_array * 32767).astype(np.int16)
        elif bit_depth == 32:
            audio_array = audio_array.astype(np.float32)
        else:
            raise ValueError(f"Unsupported bit depth: {bit_depth}")

        # Save to bytes
        with io.BytesIO() as buffer:
            sf.write(
                buffer,
                audio_array,
                samplerate=sample_rate,
                format=format,
                subtype=f'PCM_{bit_depth}' if format == 'wav' else None
            )
            return buffer.getvalue()
    except Exception as e:
        logger.error(f"Failed to save audio to bytes: {str(e)}")
        raise ValueError(f"Audio save failed: {str(e)}")


def convert_audio_format(
        audio_bytes: bytes,
        input_format: Optional[str] = None,
        output_format: str = 'wav',
        sample_rate: Optional[int] = None
) -> bytes:
    """
    Convert audio from one format to another.

    Args:
        audio_bytes: Input audio data
        input_format: Input format (None for auto-detect)
        output_format: Desired output format
        sample_rate: Optional target sample rate

    Returns:
        bytes: Converted audio data
    """
    try:
        # Load audio
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=input_format)

        # Apply sample rate conversion if needed
        if sample_rate and sample_rate != audio.frame_rate:
            audio = audio.set_frame_rate(sample_rate)

        # Convert to output format
        with io.BytesIO() as buffer:
            audio.export(
                buffer,
                format=output_format,
                codec='pcm_s16le' if output_format == 'wav' else None
            )
            return buffer.getvalue()
    except Exception as e:
        logger.error(f"Audio conversion failed: {str(e)}")
        raise ValueError(f"Audio conversion failed: {str(e)}")


def extract_text_features(audio_array: np.ndarray) -> np.ndarray:
    """
    Extract basic features from audio that could help with language detection.

    Args:
        audio_array: Input audio array

    Returns:
        np.ndarray: Extracted features
    """
    try:
        # Basic spectral features
        spectrum = np.abs(np.fft.rfft(audio_array))
        spectral_centroid = np.sum(np.arange(len(spectrum)) * spectrum) / np.sum(spectrum)
        spectral_bandwidth = np.sqrt(
            np.sum((np.arange(len(spectrum)) - spectral_centroid) ** 2 * spectrum) / np.sum(spectrum))

        # Temporal features
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_array)))) / len(audio_array)
        energy = np.sum(audio_array ** 2)

        return np.array([
            spectral_centroid,
            spectral_bandwidth,
            zero_crossings,
            energy,
            len(audio_array) / DEFAULT_SAMPLE_RATE  # duration
        ])
    except Exception as e:
        logger.warning(f"Feature extraction failed: {str(e)}")
        return np.zeros(5)  # Return zero features if extraction fails


def get_audio_duration(audio_bytes: bytes) -> float:
    """
    Get duration of audio in seconds.

    Args:
        audio_bytes: Audio data in bytes

    Returns:
        float: Duration in seconds
    """
    try:
        with sf.SoundFile(io.BytesIO(audio_bytes)) as sound_file:
            return len(sound_file) / sound_file.samplerate
    except Exception:
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            return len(audio) / 1000.0  # pydub returns milliseconds
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {str(e)}")
            return 0.0


def normalize_audio_volume(
        audio_array: np.ndarray,
        target_dBFS: float = -20.0
) -> np.ndarray:
    """
    Normalize audio volume to target dBFS.

    Args:
        audio_array: Input audio array
        target_dBFS: Target volume in dBFS

    Returns:
        np.ndarray: Normalized audio array
    """
    try:
        # Convert to pydub AudioSegment for volume normalization
        audio_segment = AudioSegment(
            audio_array.tobytes(),
            frame_rate=DEFAULT_SAMPLE_RATE,
            sample_width=audio_array.dtype.itemsize,
            channels=1
        )

        # Normalize volume
        change_in_dBFS = target_dBFS - audio_segment.dBFS
        normalized = audio_segment.apply_gain(change_in_dBFS)

        # Convert back to numpy
        return np.frombuffer(normalized.raw_data, dtype=np.float32)
    except Exception as e:
        logger.warning(f"Volume normalization failed: {str(e)}")
        return audio_array  # Return original if normalization fails


def split_audio_on_silence(
        audio_array: np.ndarray,
        silence_threshold: float = -40.0,
        min_silence_len: int = 500,
        keep_silence: int = 200
) -> list[np.ndarray]:
    """
    Split audio on silent periods.

    Args:
        audio_array: Input audio array
        silence_threshold: Threshold in dBFS to consider as silence
        min_silence_len: Minimum silence length in milliseconds to split on
        keep_silence: Amount of silence to leave at each split in milliseconds

    Returns:
        list: List of audio chunks
    """
    try:
        # Convert to pydub AudioSegment for silence splitting
        audio_segment = AudioSegment(
            audio_array.tobytes(),
            frame_rate=DEFAULT_SAMPLE_RATE,
            sample_width=audio_array.dtype.itemsize,
            channels=1
        )

        chunks = AudioSegment.silent(min_silence_len).split_on_silence(
            audio_segment,
            min_silence_len=min_silence_len,
            silence_thresh=silence_threshold,
            keep_silence=keep_silence
        )

        # Convert chunks back to numpy arrays
        return [
            np.frombuffer(chunk.raw_data, dtype=np.float32)
            for chunk in chunks
        ]
    except Exception as e:
        logger.warning(f"Audio splitting failed: {str(e)}")
        return [audio_array]  # Return original as single chunk if splitting fails
