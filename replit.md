# AI Audio Processor

## Overview

This is a Streamlit-based web application that provides AI-powered audio processing capabilities. The application allows users to upload audio files and apply various transformations including tempo control and bass boosting. It's designed as a user-friendly interface for audio manipulation using advanced signal processing techniques powered by librosa and other audio processing libraries.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid prototyping and deployment
- **Layout**: Wide layout with sidebar-based controls for audio processing parameters
- **State Management**: Streamlit session state to persist processed audio, original audio, and processor instances across user interactions
- **User Interface**: Clean, intuitive interface with emoji-enhanced headers and real-time parameter feedback

### Backend Architecture
- **Core Processing**: Object-oriented design with dedicated `AudioProcessor` class handling all audio manipulation operations
- **Audio Loading**: Leverages librosa for universal audio format support and automatic format detection
- **Signal Processing**: Implements phase vocoder-based tempo stretching with configurable quality settings
- **Multi-channel Support**: Handles both mono and stereo audio files with channel-specific processing
- **Error Handling**: Comprehensive exception handling throughout the audio processing pipeline

### Data Processing Pipeline
- **Input Validation**: File format verification and parameter validation before processing
- **Audio Loading**: Automatic sample rate detection and channel configuration preservation
- **Tempo Adjustment**: Phase vocoder implementation with quality-based hop length configuration
- **Output Generation**: In-memory audio processing with temporary file handling for downloads

### Utility Functions
- **File Management**: Helper functions for file size calculation, duration formatting, and format validation
- **Parameter Validation**: Input sanitization and range checking for processing parameters
- **User Feedback**: Processing recommendations and parameter display formatting

## External Dependencies

### Audio Processing Libraries
- **librosa**: Primary audio analysis and manipulation library for loading, tempo stretching, and audio effects
- **soundfile**: Audio file I/O operations and format conversion
- **scipy**: Signal processing utilities and mathematical operations
- **numpy**: Numerical computing foundation for audio data manipulation

### Web Framework
- **streamlit**: Core web application framework providing the user interface and session management

### System Dependencies
- **tempfile**: Temporary file creation for audio processing operations
- **pathlib**: Modern file path handling and manipulation
- **io**: In-memory file operations for audio data streaming