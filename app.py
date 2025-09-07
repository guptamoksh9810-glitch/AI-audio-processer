import streamlit as st
import os
import tempfile
import io
from pathlib import Path
from audio_processor import AudioProcessor
from video_downloader import VideoDownloader
from utils import get_file_size, format_duration, is_supported_format

# Configure page
st.set_page_config(
    page_title="AI Audio Processor",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_audio' not in st.session_state:
    st.session_state.processed_audio = None
if 'original_audio' not in st.session_state:
    st.session_state.original_audio = None
if 'processor' not in st.session_state:
    st.session_state.processor = AudioProcessor()
if 'downloader' not in st.session_state:
    st.session_state.downloader = VideoDownloader()
if 'video_info' not in st.session_state:
    st.session_state.video_info = None

def main():
    st.title("🎵 AI Audio Processor")
    st.markdown("**Create slowed, sped-up, and bass-boosted versions of your favorite songs!**")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🐌 **Slowed Versions**\nChill & relaxed vibes")
    with col2:
        st.markdown("⚡ **Sped Up Tracks**\nEnergetic & upbeat")
    with col3:
        st.markdown("💥 **Ultra Bass Boost**\nPowerful deep sound")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Audio Controls")
        
        # Tempo control
        st.subheader("🎵 Speed Control")
        
        # Preset buttons for common speeds
        st.write("**Quick Presets:**")
        col_slow, col_norm, col_fast = st.columns(3)
        
        with col_slow:
            if st.button("🐌 Slowed\n(0.75x)", use_container_width=True, help="Popular slowed version"):
                st.session_state.tempo_preset = 0.75
        
        with col_norm:
            if st.button("⏸️ Normal\n(1.0x)", use_container_width=True, help="Original speed"):
                st.session_state.tempo_preset = 1.0
        
        with col_fast:
            if st.button("⚡ Sped Up\n(1.25x)", use_container_width=True, help="Popular sped up version"):
                st.session_state.tempo_preset = 1.25
        
        # Initialize preset if not exists
        if 'tempo_preset' not in st.session_state:
            st.session_state.tempo_preset = 1.0
        
        st.write("**Custom Speed:**")
        tempo_factor = st.slider(
            "Fine Control",
            min_value=0.25,
            max_value=2.5,
            value=st.session_state.tempo_preset,
            step=0.05,
            help="Drag to set custom speed • 0.5x = Half speed • 1.5x = Fast • 2.0x+ = Very fast"
        )
        
        # Update preset when slider changes
        st.session_state.tempo_preset = tempo_factor
        
        # Enhanced display with emojis and descriptions
        if tempo_factor == 1.0:
            tempo_display = "🎵 Normal Speed"
            tempo_description = "Original tempo"
        elif tempo_factor < 0.6:
            tempo_display = f"🐌 Super Slowed ({tempo_factor}x)"
            tempo_description = "Very relaxed vibe"
        elif tempo_factor < 1.0:
            tempo_display = f"🎧 Slowed ({tempo_factor}x)"
            tempo_description = "Chill & relaxed"
        elif tempo_factor <= 1.3:
            tempo_display = f"⚡ Sped Up ({tempo_factor}x)"
            tempo_description = "Energetic & upbeat"
        else:
            tempo_display = f"🚀 Super Fast ({tempo_factor}x)"
            tempo_description = "High energy"
        
        st.write(f"**Current:** {tempo_display}")
        st.caption(tempo_description)
        
        # Bass boost control
        st.subheader("🔊 Bass Enhancement")
        
        # Bass preset buttons
        st.write("**Quick Presets:**")
        col_none, col_medium, col_ultra = st.columns(3)
        
        with col_none:
            if st.button("🎵 Clean\n(No Bass)", use_container_width=True, help="Original bass levels"):
                st.session_state.bass_preset = 0
        
        with col_medium:
            if st.button("🎸 Boosted\n(+5 dB)", use_container_width=True, help="Moderate bass boost"):
                st.session_state.bass_preset = 5
        
        with col_ultra:
            if st.button("💥 Ultra Bass\n(+10 dB)", use_container_width=True, help="Heavy bass boost"):
                st.session_state.bass_preset = 10
        
        # Initialize bass preset if not exists
        if 'bass_preset' not in st.session_state:
            st.session_state.bass_preset = 5
        
        st.write("**Custom Bass:**")
        bass_boost = st.slider(
            "Fine Control (dB)",
            min_value=0,
            max_value=15,
            value=st.session_state.bass_preset,
            step=1,
            help="0 = Original • 5 = Moderate • 10+ = Heavy bass"
        )
        
        # Update preset when slider changes
        st.session_state.bass_preset = bass_boost
        
        # Enhanced bass display
        if bass_boost == 0:
            bass_display = "🎵 No Boost (Clean)"
            bass_description = "Original bass levels"
        elif bass_boost <= 3:
            bass_display = f"🎶 Light Boost (+{bass_boost} dB)"
            bass_description = "Subtle enhancement"
        elif bass_boost <= 7:
            bass_display = f"🎸 Medium Boost (+{bass_boost} dB)"
            bass_description = "Noticeable bass bump"
        elif bass_boost <= 10:
            bass_display = f"🔊 Heavy Boost (+{bass_boost} dB)"
            bass_description = "Strong bass presence"
        else:
            bass_display = f"💥 Ultra Boost (+{bass_boost} dB)"
            bass_description = "Maximum bass power"
        
        st.write(f"**Current:** {bass_display}")
        st.caption(bass_description)
        
        # Processing quality
        st.subheader("Quality Settings")
        quality = st.selectbox(
            "Processing Quality",
            ["Standard", "High"],
            help="Higher quality takes longer but produces better results"
        )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Create tabs for upload methods
        upload_tab, url_tab = st.tabs(["📤 Upload File", "🔗 From URL"])
        
        with upload_tab:
            st.header("Upload Audio File")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=['mp3', 'wav', 'flac', 'm4a', 'ogg'],
                help="Supported formats: MP3, WAV, FLAC, M4A, OGG"
            )
            
            if uploaded_file is not None:
                # Display file info
                file_size = get_file_size(uploaded_file)
                st.success(f"✅ File uploaded: **{uploaded_file.name}** ({file_size})")
                
                # Store original audio in session state
                st.session_state.original_audio = uploaded_file
                st.session_state.video_info = None  # Clear video info
                
                # Play original audio
                st.subheader("🎧 Original Audio")
                st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
        
        with url_tab:
            st.header("Download from Video URL")
            
            # URL input
            video_url = st.text_input(
                "Enter video URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Supports YouTube, SoundCloud, TikTok, and many other platforms"
            )
            
            if video_url:
                if st.session_state.downloader.is_valid_url(video_url):
                    # Get video info button
                    if st.button("📋 Get Video Info", type="secondary"):
                        with st.spinner("Getting video information..."):
                            try:
                                info = st.session_state.downloader.get_video_info(video_url)
                                st.session_state.video_info = info
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error getting video info: {str(e)}")
                    
                    # Display video info if available
                    if st.session_state.video_info:
                        info = st.session_state.video_info
                        st.success("✅ Video information loaded!")
                        
                        # Video details
                        st.write(f"**Title:** {info['title'][:80]}{'...' if len(info['title']) > 80 else ''}")
                        st.write(f"**Duration:** {st.session_state.downloader.format_duration(info['duration'])}")
                        st.write(f"**Uploader:** {info['uploader']}")
                        
                        # Download audio button
                        if st.button("⬇️ Download Audio", type="primary"):
                            download_audio_from_url(video_url, info['title'])
                else:
                    st.warning("⚠️ Please enter a valid video URL")
            
            # Supported sites info
            with st.expander("📺 Supported Video Platforms"):
                sites_info = st.session_state.downloader.get_supported_sites_info()
                st.write("**Primary platforms:**")
                for site in sites_info['primary_sites']:
                    st.write(f"• {site}")
                st.write("**Additional platforms:**")
                for site in sites_info['additional_sites']:
                    st.write(f"• {site}")
                st.info(sites_info['note'])
    
    with col2:
        st.header("⚡ Process Audio")
        
        if st.session_state.original_audio is not None:
            # Process button
            if st.button("🚀 Process Audio", type="primary", use_container_width=True):
                process_audio(st.session_state.original_audio, tempo_factor, bass_boost, quality)
            
            # Show processed audio if available
            if st.session_state.processed_audio is not None:
                st.subheader("🎧 Processed Audio")
                st.audio(st.session_state.processed_audio, format='audio/wav')
                
                # Download button
                original_name = st.session_state.original_audio.name if hasattr(st.session_state.original_audio, 'name') else "audio"
                file_name_base = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
                st.download_button(
                    label="💾 Download Processed Audio",
                    data=st.session_state.processed_audio,
                    file_name=f"processed_{file_name_base}.wav",
                    mime="audio/wav",
                    use_container_width=True
                )
        else:
            st.info("👆 Please upload an audio file or download from a video URL first")
    
    # Processing tips
    with st.expander("💡 Processing Tips & Popular Combinations"):
        st.markdown("""
        **🎵 Popular Speed Settings:**
        - **Slowed (0.75x)**: Perfect for chill, relaxed vibes
        - **Sped Up (1.25x)**: Popular for energetic, upbeat versions
        - **Super Fast (1.5x+)**: High-energy, intense feeling
        - **Custom speeds**: Fine-tune between presets for your perfect sound
        
        **🔊 Bass Enhancement Guide:**
        - **Clean (0 dB)**: Keep original bass levels
        - **Boosted (+5 dB)**: Moderate enhancement, great for most songs
        - **Ultra Bass (+10 dB)**: Heavy bass for that deep, powerful sound
        - **Custom levels**: Adjust to match your style preference
        
        **🎯 Popular Combinations:**
        - **Slowed + Ultra Bass**: The viral "slowed + reverb" effect
        - **Sped Up + Clean Bass**: Energetic without overpowering bass
        - **Normal Speed + Boosted Bass**: Enhanced original with better bass
        
        **⚙️ Quality Settings:**
        - **Standard**: Faster processing, good quality (recommended)
        - **High**: Slower processing, maximum quality (for special tracks)
        """)

def process_audio(uploaded_file, tempo_factor, bass_boost, quality):
    """Process the uploaded audio file with specified settings"""
    try:
        # Show processing status
        with st.spinner("🔄 Processing audio... This may take a moment."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                input_path = tmp_file.name
            
            status_text.text("Loading audio file...")
            progress_bar.progress(20)
            
            # Load audio
            audio_data, sample_rate = st.session_state.processor.load_audio(input_path)
            
            status_text.text("Applying tempo changes...")
            progress_bar.progress(40)
            
            # Apply tempo change
            if tempo_factor != 1.0:
                audio_data = st.session_state.processor.change_tempo(audio_data, tempo_factor, quality)
            
            status_text.text("Boosting bass frequencies...")
            progress_bar.progress(70)
            
            # Apply bass boost
            if bass_boost > 0:
                audio_data = st.session_state.processor.boost_bass(audio_data, sample_rate, bass_boost)
            
            status_text.text("Saving processed audio...")
            progress_bar.progress(90)
            
            # Convert to bytes for download
            output_buffer = io.BytesIO()
            st.session_state.processor.save_audio(audio_data, sample_rate, output_buffer)
            processed_audio_bytes = output_buffer.getvalue()
            
            # Store in session state
            st.session_state.processed_audio = processed_audio_bytes
            
            progress_bar.progress(100)
            status_text.text("✅ Processing complete!")
            
            # Clean up temporary file
            os.unlink(input_path)
            
            st.success("🎉 Audio processed successfully!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error processing audio: {str(e)}")
        st.error("Please try with a different file or adjust the settings.")

def download_audio_from_url(video_url, video_title):
    """Download audio from video URL and prepare for processing"""
    try:
        # Show download status
        with st.spinner("🔄 Downloading audio... This may take a moment."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Getting video information...")
            progress_bar.progress(20)
            
            # Download audio using the video downloader
            temp_dir = tempfile.mkdtemp()
            
            status_text.text("Downloading audio from video...")
            progress_bar.progress(60)
            
            audio_file_path = st.session_state.downloader.download_audio(video_url, temp_dir)
            
            status_text.text("Converting audio for processing...")
            progress_bar.progress(80)
            
            # Read the downloaded audio file as bytes
            with open(audio_file_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Create a file-like object that mimics uploaded file
            class AudioFile:
                def __init__(self, data, name):
                    self._data = data
                    self.name = name
                
                def getvalue(self):
                    return self._data
                
                def read(self):
                    return self._data
            
            # Clean filename for processing
            safe_filename = f"{video_title[:50]}.wav"
            downloaded_audio = AudioFile(audio_bytes, safe_filename)
            
            # Store as original audio for processing
            st.session_state.original_audio = downloaded_audio
            st.session_state.video_info = None  # Clear video info after download
            
            # Clean up temporary files
            st.session_state.downloader.cleanup_temp_files(temp_dir)
            
            progress_bar.progress(100)
            status_text.text("✅ Audio downloaded successfully!")
            
            st.success("🎉 Audio downloaded and ready for processing!")
            
            # Show audio player
            st.subheader("🎧 Downloaded Audio")
            st.audio(audio_bytes, format='audio/wav')
            
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error downloading audio: {str(e)}")
        st.error("Please check the URL and try again.")

if __name__ == "__main__":
    main()
