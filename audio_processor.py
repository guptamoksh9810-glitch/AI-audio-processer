import librosa
import numpy as np
import soundfile as sf
import scipy.signal
from scipy import signal
import io
import tempfile
import os

class AudioProcessor:
    def __init__(self):
        self.supported_formats = ['mp3', 'wav', 'flac', 'm4a', 'ogg']
    
    def load_audio(self, file_path):
        """Load audio file and return audio data and sample rate"""
        try:
            # Load audio with librosa (automatically handles various formats)
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=False)
            
            # If stereo, keep both channels
            if len(audio_data.shape) == 1:
                # Mono audio
                return audio_data, sample_rate
            else:
                # Stereo audio - librosa loads as (channels, samples)
                return audio_data, sample_rate
                
        except Exception as e:
            raise Exception(f"Failed to load audio file: {str(e)}")
    
    def change_tempo(self, audio_data, tempo_factor, quality="Standard"):
        """Change the tempo of audio using phase vocoder"""
        try:
            # Set hop length based on quality
            hop_length = 256 if quality == "High" else 512
            
            if len(audio_data.shape) == 1:
                # Mono audio
                stretched_audio = librosa.effects.time_stretch(
                    audio_data, 
                    rate=tempo_factor,
                    hop_length=hop_length
                )
            else:
                # Stereo audio - process each channel separately
                stretched_channels = []
                for channel in audio_data:
                    stretched_channel = librosa.effects.time_stretch(
                        channel,
                        rate=tempo_factor,
                        hop_length=hop_length
                    )
                    stretched_channels.append(stretched_channel)
                stretched_audio = np.array(stretched_channels)
            
            return stretched_audio
            
        except Exception as e:
            raise Exception(f"Failed to change tempo: {str(e)}")
    
    def boost_bass(self, audio_data, sample_rate, boost_db):
        """Apply bass boost using a low-shelf filter"""
        try:
            # Design a low-shelf filter for bass boost
            # Bass frequencies: 20-250 Hz, with peak around 60-80 Hz
            freq_cutoff = 250  # Hz
            
            # Convert dB to linear gain
            gain_linear = 10**(boost_db / 20.0)
            
            # Design low-shelf filter
            sos = signal.butter(
                N=2,  # Filter order
                Wn=freq_cutoff / (sample_rate / 2),  # Normalized frequency
                btype='low',
                output='sos'
            )
            
            if len(audio_data.shape) == 1:
                # Mono audio
                # Apply filter to boost bass
                bass_boosted = signal.sosfilt(sos, audio_data)
                # Mix with original (controlled bass boost)
                mixed_audio = audio_data + (bass_boosted - audio_data) * (gain_linear - 1)
                # Normalize to prevent clipping
                return self.normalize_audio(mixed_audio)
            else:
                # Stereo audio
                boosted_channels = []
                for channel in audio_data:
                    bass_boosted = signal.sosfilt(sos, channel)
                    mixed_channel = channel + (bass_boosted - channel) * (gain_linear - 1)
                    boosted_channels.append(self.normalize_audio(mixed_channel))
                return np.array(boosted_channels)
                
        except Exception as e:
            raise Exception(f"Failed to boost bass: {str(e)}")
    
    def normalize_audio(self, audio_data, target_peak=0.95):
        """Normalize audio to prevent clipping"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data * (target_peak / max_val)
        return audio_data
    
    def save_audio(self, audio_data, sample_rate, output_buffer):
        """Save audio data to a buffer in WAV format"""
        try:
            # Ensure audio is in the correct format for soundfile
            if len(audio_data.shape) == 1:
                # Mono audio
                sf.write(output_buffer, audio_data, sample_rate, format='WAV')
            else:
                # Stereo audio - transpose to (samples, channels) for soundfile
                audio_transposed = audio_data.T
                sf.write(output_buffer, audio_transposed, sample_rate, format='WAV')
            
            output_buffer.seek(0)  # Reset buffer position
            
        except Exception as e:
            raise Exception(f"Failed to save audio: {str(e)}")
    
    def get_audio_info(self, file_path):
        """Get basic information about an audio file"""
        try:
            info = sf.info(file_path)
            return {
                'duration': info.frames / info.samplerate,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format
            }
        except Exception as e:
            return None
    
    def apply_high_quality_bass_boost(self, audio_data, sample_rate, boost_db):
        """Apply a more sophisticated bass boost using parametric EQ"""
        try:
            # Multiple frequency bands for better bass enhancement
            bass_frequencies = [60, 120, 180]  # Hz
            q_factor = 0.7  # Quality factor for the filter
            
            processed_audio = audio_data.copy()
            
            for freq in bass_frequencies:
                # Create a peaking EQ filter for each bass frequency
                nyquist = sample_rate / 2
                normalized_freq = freq / nyquist
                
                # Design peaking filter
                b, a = signal.iirpeak(normalized_freq, Q=q_factor)
                
                if len(audio_data.shape) == 1:
                    # Mono audio
                    filtered = signal.filtfilt(b, a, processed_audio)
                    # Apply boost
                    gain = 10**(boost_db / 20.0)
                    processed_audio = processed_audio + (filtered - processed_audio) * (gain - 1) * 0.3
                else:
                    # Stereo audio
                    for i, channel in enumerate(processed_audio):
                        filtered = signal.filtfilt(b, a, channel)
                        gain = 10**(boost_db / 20.0)
                        processed_audio[i] = channel + (filtered - channel) * (gain - 1) * 0.3
            
            return self.normalize_audio(processed_audio)
            
        except Exception as e:
            # Fallback to simple bass boost
            return self.boost_bass(audio_data, sample_rate, boost_db)
