// Global variables
let audioContext;
let audioBuffer;
let originalAudioData;
let currentTempo = 1.0;
let currentBass = 5;
let processedAudioBlob = null;

// Initialize Web Audio API
function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
}

// Tab switching
function switchTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab
    if (tabName === 'upload') {
        document.querySelector('.tab-btn:first-child').classList.add('active');
        document.getElementById('uploadTab').classList.add('active');
    } else {
        document.querySelector('.tab-btn:last-child').classList.add('active');
        document.getElementById('urlTab').classList.add('active');
    }
}

// Tempo control functions
function setTempo(value) {
    currentTempo = value;
    document.getElementById('tempoSlider').value = value;
    updateTempoDisplay(value);
}

function updateTempo(value) {
    currentTempo = parseFloat(value);
    updateTempoDisplay(currentTempo);
}

function updateTempoDisplay(tempo) {
    const display = document.getElementById('tempoDisplay');
    const description = document.getElementById('tempoDescription');
    
    if (tempo === 1.0) {
        display.textContent = "🎵 Normal Speed";
        description.textContent = "Original tempo";
    } else if (tempo < 0.6) {
        display.textContent = `🐌 Super Slowed (${tempo}x)`;
        description.textContent = "Very relaxed vibe";
    } else if (tempo < 1.0) {
        display.textContent = `🎧 Slowed (${tempo}x)`;
        description.textContent = "Chill & relaxed";
    } else if (tempo <= 1.3) {
        display.textContent = `⚡ Sped Up (${tempo}x)`;
        description.textContent = "Energetic & upbeat";
    } else {
        display.textContent = `🚀 Super Fast (${tempo}x)`;
        description.textContent = "High energy";
    }
}

// Bass control functions
function setBass(value) {
    currentBass = value;
    document.getElementById('bassSlider').value = value;
    updateBassDisplay(value);
}

function updateBass(value) {
    currentBass = parseInt(value);
    updateBassDisplay(currentBass);
}

function updateBassDisplay(bass) {
    const display = document.getElementById('bassDisplay');
    const description = document.getElementById('bassDescription');
    
    if (bass === 0) {
        display.textContent = "🎵 No Boost (Clean)";
        description.textContent = "Original bass levels";
    } else if (bass <= 3) {
        display.textContent = `🎶 Light Boost (+${bass} dB)`;
        description.textContent = "Subtle enhancement";
    } else if (bass <= 7) {
        display.textContent = `🎸 Medium Boost (+${bass} dB)`;
        description.textContent = "Noticeable bass bump";
    } else if (bass <= 10) {
        display.textContent = `🔊 Heavy Boost (+${bass} dB)`;
        description.textContent = "Strong bass presence";
    } else {
        display.textContent = `💥 Ultra Boost (+${bass} dB)`;
        description.textContent = "Maximum bass power";
    }
}

// File upload handling
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Show file info
    const fileInfo = document.getElementById('fileInfo');
    const fileSize = (file.size / (1024 * 1024)).toFixed(2);
    fileInfo.innerHTML = `
        <strong>✅ File uploaded:</strong> ${file.name} (${fileSize} MB)
    `;
    fileInfo.style.display = 'block';
    
    // Load audio file
    loadAudioFile(file);
    
    // Hide info message and enable process button
    document.getElementById('infoMessage').style.display = 'none';
    document.getElementById('processBtn').disabled = false;
}

// Load audio file into Web Audio API
function loadAudioFile(file) {
    initAudioContext();
    
    const reader = new FileReader();
    reader.onload = function(e) {
        audioContext.decodeAudioData(e.target.result)
            .then(buffer => {
                audioBuffer = buffer;
                originalAudioData = buffer;
                
                // Show original audio player
                const originalSection = document.getElementById('originalAudio');
                const originalPlayer = document.getElementById('originalPlayer');
                
                const blob = new Blob([e.target.result], { type: file.type });
                const url = URL.createObjectURL(blob);
                originalPlayer.src = url;
                originalSection.style.display = 'block';
            })
            .catch(error => {
                console.error('Error decoding audio:', error);
                alert('Error loading audio file. Please try a different file.');
            });
    };
    reader.readAsArrayBuffer(file);
}

// URL input handling (limited functionality)
function handleUrlInput() {
    const url = document.getElementById('videoUrl').value.trim();
    if (!url) {
        alert('Please enter a video URL');
        return;
    }
    
    // Show limitation message
    alert('Video downloading requires server-side processing. For full URL functionality, please use our server-based version or download the audio manually and upload the file.');
}

// Process audio with tempo and bass adjustments
async function processAudio() {
    if (!audioBuffer) {
        alert('Please upload an audio file first');
        return;
    }
    
    // Show processing status
    const statusDiv = document.getElementById('processingStatus');
    const statusText = document.getElementById('statusText');
    const processBtn = document.getElementById('processBtn');
    
    statusDiv.style.display = 'block';
    processBtn.disabled = true;
    
    try {
        statusText.textContent = 'Initializing processing...';
        await new Promise(resolve => setTimeout(resolve, 500));
        
        statusText.textContent = 'Applying tempo changes...';
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Create a new buffer for processed audio
        let processedBuffer = audioBuffer;
        
        // Apply tempo change (simplified - this is a basic implementation)
        if (currentTempo !== 1.0) {
            processedBuffer = await changeAudioTempo(audioBuffer, currentTempo);
        }
        
        statusText.textContent = 'Enhancing bass frequencies...';
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Apply bass boost (simplified EQ)
        if (currentBass > 0) {
            processedBuffer = await boostBass(processedBuffer, currentBass);
        }
        
        statusText.textContent = 'Finalizing audio...';
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Convert processed buffer to blob for download
        const processedArrayBuffer = await audioBufferToWav(processedBuffer);
        processedAudioBlob = new Blob([processedArrayBuffer], { type: 'audio/wav' });
        
        // Show processed audio player
        const processedSection = document.getElementById('processedAudio');
        const processedPlayer = document.getElementById('processedPlayer');
        
        const url = URL.createObjectURL(processedAudioBlob);
        processedPlayer.src = url;
        processedSection.style.display = 'block';
        
        statusText.textContent = '✅ Processing complete!';
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        statusDiv.style.display = 'none';
        processBtn.disabled = false;
        
    } catch (error) {
        console.error('Processing error:', error);
        alert('Error processing audio. Please try again.');
        statusDiv.style.display = 'none';
        processBtn.disabled = false;
    }
}

// Simplified tempo change (basic implementation)
async function changeAudioTempo(buffer, tempoFactor) {
    const sampleRate = buffer.sampleRate;
    const channels = buffer.numberOfChannels;
    const length = Math.floor(buffer.length / tempoFactor);
    
    const newBuffer = audioContext.createBuffer(channels, length, sampleRate);
    
    for (let channel = 0; channel < channels; channel++) {
        const inputData = buffer.getChannelData(channel);
        const outputData = newBuffer.getChannelData(channel);
        
        for (let i = 0; i < length; i++) {
            const sourceIndex = Math.floor(i * tempoFactor);
            if (sourceIndex < inputData.length) {
                outputData[i] = inputData[sourceIndex];
            }
        }
    }
    
    return newBuffer;
}

// Simplified bass boost (basic EQ)
async function boostBass(buffer, boostDb) {
    const sampleRate = buffer.sampleRate;
    const channels = buffer.numberOfChannels;
    const length = buffer.length;
    
    const newBuffer = audioContext.createBuffer(channels, length, sampleRate);
    const gain = Math.pow(10, boostDb / 20); // Convert dB to linear gain
    
    for (let channel = 0; channel < channels; channel++) {
        const inputData = buffer.getChannelData(channel);
        const outputData = newBuffer.getChannelData(channel);
        
        // Simple bass boost: amplify lower frequencies (this is very basic)
        for (let i = 0; i < length; i++) {
            // Apply a simple low-pass boost (not a proper EQ, but gives bass effect)
            let sample = inputData[i];
            if (i > 0) {
                sample = (sample + inputData[i-1] * 0.5) * gain * 0.7;
            }
            outputData[i] = Math.max(-1, Math.min(1, sample)); // Prevent clipping
        }
    }
    
    return newBuffer;
}

// Convert AudioBuffer to WAV ArrayBuffer
async function audioBufferToWav(buffer) {
    const length = buffer.length;
    const numberOfChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    
    const arrayBuffer = new ArrayBuffer(44 + length * numberOfChannels * 2);
    const view = new DataView(arrayBuffer);
    
    // WAV header
    const writeString = (offset, string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + length * numberOfChannels * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numberOfChannels * 2, true);
    view.setUint16(32, numberOfChannels * 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, length * numberOfChannels * 2, true);
    
    // Convert float samples to 16-bit PCM
    let offset = 44;
    for (let i = 0; i < length; i++) {
        for (let channel = 0; channel < numberOfChannels; channel++) {
            const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
            view.setInt16(offset, sample * 0x7FFF, true);
            offset += 2;
        }
    }
    
    return arrayBuffer;
}

// Download processed audio
function downloadProcessedAudio() {
    if (!processedAudioBlob) {
        alert('No processed audio available for download');
        return;
    }
    
    const url = URL.createObjectURL(processedAudioBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'processed_audio.wav';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Set initial values
    updateTempoDisplay(1.0);
    updateBassDisplay(5);
    
    // Add drag and drop functionality
    const fileUpload = document.getElementById('fileUpload');
    
    fileUpload.addEventListener('dragover', function(e) {
        e.preventDefault();
        fileUpload.style.borderColor = '#667eea';
        fileUpload.style.background = 'rgba(102, 126, 234, 0.1)';
    });
    
    fileUpload.addEventListener('dragleave', function(e) {
        e.preventDefault();
        fileUpload.style.borderColor = '#ccc';
        fileUpload.style.background = 'transparent';
    });
    
    fileUpload.addEventListener('drop', function(e) {
        e.preventDefault();
        fileUpload.style.borderColor = '#ccc';
        fileUpload.style.background = 'transparent';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            document.getElementById('audioFile').files = files;
            handleFileUpload({ target: { files: files } });
        }
    });
});