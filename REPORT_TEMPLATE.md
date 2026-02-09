# TinyWorld AI Hackathon Report

**Project Name:** Offline OCR
**Team Name:** [Your Team Name]

## 1. Problem Statement
Build an offline text reading tool that runs on low-end devices with no internet access and strict model size limits (<10MB).

## 2. Solution Overview
We developed a modular OCR pipeline in Python using standard libraries.
- **Image Processing**: OpenCV for adaptive thresholding and noise reduction.
- **Segmentation**: Contour-based detection sorted by line and character position.
- **Recognition**: A custom-trained Linear SVM model (scikit-learn) trained on synthetic font data.
- **UI**: A responsive tkinter interface.

## 3. Key Metrics
- **Model Size**: [Insert Size, e.g., 0.5 MB] (Limit: 10MB)
- **Inference Time**: [Insert Time, e.g., 0.8s] (Limit: 2s)
- **Offline**: Yes (100%)

## 4. Technical Architecture
[Provide a simple diagram or description of the pipeline]
Input Image -> Preprocessing -> Segmentation -> Classification -> Post-processing -> Text Output.

## 5. Challenges & Solutions
- **Model Size**: We used LinearSVM instead of CNNs/Transformers to keep the model tiny.
- **Data**: We generated synthetic character data using PIL since external datasets were too large/complex to manage offline easily.

## 6. Future Improvements
- Better handwriting support.
- More robust line segmentation for complex layouts.
