# Emoji Reactor

A real-time camera-based emoji display application that uses MediaPipe to detect your poses and facial expressions, then displays corresponding monkey imahe in a separate window.

## Requirements

- Python 3.12 (Homebrew: `brew install python@3.12`)
- macOS or Windows with a webcam
- Required Python packages (see `requirements.txt`)

## Installation

1. **Clone or download this project**

2. **Create a virtual environment (Python 3.12) and install deps:**

   ```bash
   # macOS: ensure Python 3.12 is installed
   brew install python@3.12

   # Create and activate a virtual environment
   python3.12 -m venv emoji_env
   source emoji_env/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Ensure you have the monkey emoji images in the project directory:**
   - `monkey-figured.jpg` - Figured it out pose (finger up + smile)
   - `monkey-thinking.jpg` - Thinking pose (finger near mouth)
   - `monkey-straight.jpg` - Straight face (neutral expression)

## Usage

1. **Run the application:**

   ```bash
   # Option A: use helper script
   ./run.sh

   # Option B: run manually
   source emoji_env/bin/activate
   python emoji_reactor.py
   ```

2. **Two windows will open:**

- **Camera Feed**: Shows your live camera with detection status and hand landmarks
- **Emoji Output**: Displays the corresponding monkey image based on your actions

3. **Controls:**

- Press `q` to quit the application
- Hold finger near your mouth for thinking monkey
- Smile with finger raised above eye level for figured monkey
- Keep a normal face for straight face monkey

## How It Works

The application uses two MediaPipe solutions to track your hand position and facial expression simultaneously[web:22][web:24][web:9]:

1. **Hand Tracking**: Detects 21 hand landmarks, tracking your index finger tip (landmark 8) position[web:22][web:24]
2. **Face Mesh Detection**: Analyzes facial landmarks to detect smile and track reference points (eyes, nose, mouth)[web:9][web:26]

### Detection Logic

The app determines which monkey emoji to display based on finger position and facial expression[web:24][web:26]:

1. **Figured** (💡) - Requires BOTH conditions:

- You are smiling (mouth aspect ratio > 0.35)
- Index finger is positioned above eye level[web:22][web:26]

2. **Thinking** (🤔) - Detected when:

- Index finger is within 15% vertical distance of mouth
- Finger is horizontally aligned with face center (within 25% frame width)[web:24][web:28]

3. **Straight Face** (😐) - Default state when neither condition is met

### Coordinate System

MediaPipe uses normalized coordinates (0-1 range) where (0,0) is top-left and (1,1) is bottom-right[web:26]. The y-coordinate increases downward, so lower y values mean higher positions on screen[web:26].

## Customization

### Adjusting Smile Sensitivity

Edit the `SMILE_THRESHOLD` value in `emoji_reactor.py`:

- Decrease value (e.g., 0.30) if smiles aren't detected
- Increase value (e.g., 0.40) if false positive smiles occur

### Adjusting Finger Detection Zones

Modify these thresholds in the code:

- **Thinking zone**: Change `mouth_distance < 0.15` (vertical threshold)
- **Thinking zone**: Change `horizontal_distance < 0.25` (horizontal threshold)
- Lower values make detection more strict, higher values more lenient

### Changing Emoji Images

Replace the image files with your own:

- `monkey-figured.jpg` - Your "figured it out" image
- `monkey-thinking.jpg` - Your "thinking" image
- `monkey-straight.jpg` - Your "neutral" image

## Troubleshooting

### Camera Issues (macOS)

- If you see "not authorized to capture video", grant Camera access for your terminal/editor:
- System Settings → Privacy & Security → Camera → enable for Terminal/VS Code/iTerm
- Quit and relaunch the terminal/editor after changing permissions
- Ensure no other app is using the camera
- Try different camera indices by changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

### Emoji Images Not Loading

- Verify image files are in the same directory as the script
- Check file names match exactly: `monkey-figured.jpg`, `monkey-thinking.jpg`, `monkey-straight.jpg`
- Ensure image files are not corrupted (JPG/PNG format)

### Detection Issues

**Hand not detected:**

- Ensure good lighting on your hand
- Keep your hand clearly visible and within camera frame
- MediaPipe works best with open palms facing the camera[web:22][web:24]

**Smile not detected:**

- Ensure good lighting on your face
- Keep your face clearly visible in the camera
- Adjust `SMILE_THRESHOLD` if needed (default: 0.35)

**Finger position not triggering states:**

- Make deliberate gestures - hold finger clearly near mouth or above eyes
- Check the camera feed window to see if hand landmarks are being drawn
- Adjust distance thresholds if detection is too strict/lenient

## Technical Details

- Uses OpenCV for camera capture and display[web:7][web:10]
- MediaPipe Face Mesh for facial landmark detection (468 points)[web:9]
- MediaPipe Hands for hand landmark detection (21 points per hand)[web:22][web:24]
- Real-time RGB conversion and landmark tracking[web:26]
- Normalized coordinate system for resolution-independent detection[web:26]

## Dependencies

- `opencv-python` - Computer vision library for camera and display
- `mediapipe` - Google's ML solution for Hand and Face Mesh detection
- `numpy` - Numerical computing for coordinate calculations

See `requirements.txt` for installation and `requirements-lock.txt` for pinned versions.

## License

MIT License - see LICENSE file for details.