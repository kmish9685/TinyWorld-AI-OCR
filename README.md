# TinyWorld AI - Offline OCR

A lightweight, offline Optical Character Recognition (OCR) tool built for the TinyWorld AI Hackathon.

## Features
- **Offline & Lightweight**: Uses a custom trained scikit-learn model (<10MB).
- **Fast**: Inference latency < 2 seconds.
- **No Heavy Dependencies**: Built with OpenCV, NumPy, scikit-learn, and tkinter.
- **Clean UI**: Modern, simple interface for easy usage.

## Setup
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Train the Model** (First time only):
    ```bash
    python train_model.py
    ```
    This generates `data/char_model.pkl`.

## Usage
Run the application:
```bash
python main.py
```
1.  Click **Upload Image** to select an image containing text.
2.  Click **Extract Text** to process.
3.  View and save the results.

## Project Structure
- `src/`: Source code modules (preprocessing, segmentation, recognition, UI).
- `data/`: Stores the trained model.
- `train_model.py`: Script to generate synthetic data and train the model.
- `main.py`: Entry point.

## License
MIT License.
