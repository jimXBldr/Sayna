package com.sayna;

import android.app.Service;
import android.content.Intent;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.IBinder;
import android.os.Binder;
import android.util.Log;
import androidx.annotation.Nullable;

import com.sayna.utils.AudioRecorder;
import com.sayna.utils.NetworkUtils;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

public class VoiceService extends Service {
    private static final String TAG = "VoiceService";
    private static final int SAMPLE_RATE = 16000; // 16kHz
    private static final int CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO;
    private static final int AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT;
    private static final int BUFFER_SIZE = AudioRecord.getMinBufferSize(
            SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT
    );

    // Binder given to clients
    private final IBinder binder = new LocalBinder();
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final AtomicBoolean isRecording = new AtomicBoolean(false);

    private AudioRecord audioRecord;
    private VoiceServiceListener listener;
    private AudioRecorder audioRecorder;
    private String currentLanguage = "en"; // Default to English

    public interface VoiceServiceListener {
        void onRecordingStarted();
        void onRecordingStopped();
        void onAudioProcessed(String transcript, String intent, String[] actions);
        void onError(String errorMessage);
    }

    public class LocalBinder extends Binder {
        public VoiceService getService() {
            return VoiceService.this;
        }
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return binder;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "VoiceService created");
        audioRecorder = new AudioRecorder(BUFFER_SIZE);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "VoiceService started");
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        stopRecording();
        executor.shutdown();
        Log.d(TAG, "VoiceService destroyed");
    }

    public void setListener(VoiceServiceListener listener) {
        this.listener = listener;
    }

    public void setLanguage(String languageCode) {
        if (languageCode != null && !languageCode.isEmpty()) {
            this.currentLanguage = languageCode;
            Log.d(TAG, "Language set to: " + languageCode);
        }
    }

    public void startRecording() {
        if (isRecording.get()) {
            Log.w(TAG, "Recording already in progress");
            return;
        }

        executor.execute(() -> {
            try {
                isRecording.set(true);
                audioRecord = new AudioRecord(
                        MediaRecorder.AudioSource.VOICE_RECOGNITION,
                        SAMPLE_RATE,
                        CHANNEL_CONFIG,
                        AUDIO_FORMAT,
                        BUFFER_SIZE
                );

                if (audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                    throw new IllegalStateException("AudioRecord initialization failed");
                }

                audioRecord.startRecording();
                audioRecorder.reset();

                if (listener != null) {
                    runOnMainThread(() -> listener.onRecordingStarted());
                }

                Log.d(TAG, "Recording started");
                byte[] buffer = new byte[BUFFER_SIZE];

                while (isRecording.get()) {
                    int bytesRead = audioRecord.read(buffer, 0, buffer.length);
                    if (bytesRead > 0) {
                        audioRecorder.write(buffer, bytesRead);
                    }
                }

            } catch (Exception e) {
                Log.e(TAG, "Recording error: " + e.getMessage());
                if (listener != null) {
                    runOnMainThread(() -> listener.onError(e.getMessage()));
                }
            } finally {
                stopAudioRecord();
            }
        });
    }

    public void stopRecording() {
        if (!isRecording.getAndSet(false)) {
            Log.w(TAG, "No recording in progress");
            return;
        }

        executor.execute(() -> {
            try {
                byte[] audioData = audioRecorder.getRecordedData();
                if (audioData.length > 0) {
                    processAudio(audioData);
                }
            } catch (Exception e) {
                Log.e(TAG, "Error processing audio: " + e.getMessage());
                if (listener != null) {
                    runOnMainThread(() -> listener.onError(e.getMessage()));
                }
            } finally {
                if (listener != null) {
                    runOnMainThread(() -> listener.onRecordingStopped());
                }
                Log.d(TAG, "Recording stopped");
            }
        });
    }

    private void processAudio(byte[] audioData) {
        if (!NetworkUtils.isNetworkAvailable(this)) {
            processOffline(audioData);
            return;
        }

        try {
            // TODO: Implement actual API call to SAYNA backend
            // This is a mock implementation for demonstration
            String mockResponse = "{"
                    + "\"transcript\":\"Sample transcript\","
                    + "\"intent\":\"create_invoice\","
                    + "\"actions\":[\"quickbooks.create_invoice\",\"whatsapp.send_notification\"]"
                    + "}";

            // Simulate network delay
            Thread.sleep(1000);

            if (listener != null) {
                runOnMainThread(() -> {
                    listener.onAudioProcessed(
                            "Sample transcript",
                            "create_invoice",
                            new String[]{"quickbooks.create_invoice", "whatsapp.send_notification"}
                    );
                });
            }
        } catch (Exception e) {
            Log.e(TAG, "Network processing error: " + e.getMessage());
            if (listener != null) {
                runOnMainThread(() -> listener.onError(e.getMessage()));
            }
        }
    }

    private void processOffline(byte[] audioData) {
        try {
            // TODO: Implement actual offline processing
            // This is a mock implementation for demonstration
            Thread.sleep(500); // Simulate processing delay

            if (listener != null) {
                runOnMainThread(() -> {
                    listener.onAudioProcessed(
                            "Offline transcript",
                            "unknown",
                            new String[]{"offline.save_for_later"}
                    );
                });
            }
        } catch (Exception e) {
            Log.e(TAG, "Offline processing error: " + e.getMessage());
            if (listener != null) {
                runOnMainThread(() -> listener.onError(e.getMessage()));
            }
        }
    }

    private void stopAudioRecord() {
        if (audioRecord != null) {
            try {
                if (audioRecord.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) {
                    audioRecord.stop();
                }
                audioRecord.release();
            } catch (Exception e) {
                Log.e(TAG, "Error stopping AudioRecord: " + e.getMessage());
            } finally {
                audioRecord = null;
            }
        }
    }

    private void runOnMainThread(Runnable runnable) {
        new android.os.Handler(getMainLooper()).post(runnable);
    }
}