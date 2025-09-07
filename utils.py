import os
from pathlib import Path

def get_file_size(uploaded_file):
    """Get human-readable file size"""
    size_bytes = len(uploaded_file.getvalue())
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds):
    """Format duration in seconds to MM:SS format"""
    if seconds is None:
        return "Unknown"
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def is_supported_format(filename):
    """Check if the file format is supported"""
    supported_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
    file_extension = Path(filename).suffix.lower()
    return file_extension in supported_extensions

def validate_audio_parameters(tempo_factor, bass_boost):
    """Validate audio processing parameters"""
    errors = []
    
    if not (0.1 <= tempo_factor <= 3.0):
        errors.append("Tempo factor must be between 0.1 and 3.0")
    
    if not (0 <= bass_boost <= 20):
        errors.append("Bass boost must be between 0 and 20 dB")
    
    return errors

def get_processing_recommendations(tempo_factor, bass_boost):
    """Get recommendations based on processing parameters"""
    recommendations = []
    
    if tempo_factor < 0.5:
        recommendations.append("⚠️ Very slow tempo may result in artifacts. Consider using 0.5x or higher.")
    
    if tempo_factor > 1.5:
        recommendations.append("⚠️ Very fast tempo may cause quality degradation. Consider using 1.5x or lower.")
    
    if bass_boost > 10:
        recommendations.append("⚠️ High bass boost may cause distortion. Consider using 10 dB or lower.")
    
    if tempo_factor < 1.0 and bass_boost > 5:
        recommendations.append("💡 Slowed songs with bass boost create that popular 'slowed + reverb' effect!")
    
    return recommendations

def estimate_processing_time(file_size_mb, tempo_factor, bass_boost, quality):
    """Estimate processing time based on parameters"""
    base_time = file_size_mb * 0.5  # Base processing time per MB
    
    # Tempo change adds processing time
    if tempo_factor != 1.0:
        base_time *= 1.5
    
    # Bass boost adds minimal time
    if bass_boost > 0:
        base_time *= 1.1
    
    # Quality setting affects time
    if quality == "High":
        base_time *= 1.5
    
    return max(base_time, 2.0)  # Minimum 2 seconds

def create_audio_visualization_data(audio_data, sample_rate, max_points=1000):
    """Create data for audio waveform visualization"""
    try:
        # Downsample for visualization if needed
        if len(audio_data) > max_points:
            step = len(audio_data) // max_points
            audio_data = audio_data[::step]
        
        # Create time axis
        time_axis = list(range(len(audio_data)))
        
        # If stereo, take the mean of both channels
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=0)
        
        return time_axis, audio_data.tolist()
    
    except Exception:
        return [], []
