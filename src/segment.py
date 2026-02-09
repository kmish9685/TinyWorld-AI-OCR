import cv2
import numpy as np

def detect_lines(binary_image, debug_image=None):
    """
    Step 4 & 5: Text Region Detection & Line Segmentation.
    Reverted to stable baseline: Standard Canny + Dilation + Contours.
    """
    # 1. Canny Edge Detection
    edges = cv2.Canny(binary_image, 30, 150)
    
    # 2. Dilation to connect text strokes
    # Standard horizontal kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # 3. Find Contours (Lines)
    cnts, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    lines = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w < 20 or h < 10: continue
        lines.append((x, y, w, h))
        
        if debug_image is not None:
             cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 4. Sort lines top-to-bottom
    lines.sort(key=lambda b: b[1])
    return lines

def segment_chars_from_line(binary_line_region):
    """
    Step 6: Character Segmentation with Smart Filtering.
    """
    # NO DILATION - prevents character merging
    cnts, _ = cv2.findContours(binary_line_region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    raw_boxes = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        
        # Filter 1: Minimum size (remove noise)
        if w < 3 or h < 8:
            continue
            
        # Filter 2: Aspect ratio (remove fragments and merged chars)
        aspect = w / float(h)
        if aspect > 3.0:  # Too wide = merged characters
            continue
        if aspect < 0.1:  # Too thin = vertical line artifact
            continue
            
        # Filter 3: Maximum size (remove full-line boxes)
        if w > 100 or h > 100:
            continue
            
        raw_boxes.append([x, y, w, h])
    
    # Merge overlapping boxes (handles split characters like "W" → "V V")
    merged_boxes = merge_overlapping_boxes(raw_boxes)
    
    # Convert to expected format
    chars = [(x, y, w, h, 0, 0) for x, y, w, h in merged_boxes]
    chars.sort(key=lambda b: b[0])
    return chars

def merge_overlapping_boxes(boxes):
    """Merge boxes that overlap horizontally by >30%"""
    if not boxes:
        return []
        
    boxes = sorted(boxes, key=lambda b: b[0])  # Sort by x
    merged = [boxes[0]]
    
    for current in boxes[1:]:
        last = merged[-1]
        
        # Check horizontal overlap
        overlap_start = max(last[0], current[0])
        overlap_end = min(last[0] + last[2], current[0] + current[2])
        overlap_width = max(0, overlap_end - overlap_start)
        
        min_width = min(last[2], current[2])
        overlap_ratio = overlap_width / min_width if min_width > 0 else 0
        
        # Also check vertical alignment (must be on same line)
        y_diff = abs(last[1] - current[1])
        
        if overlap_ratio > 0.3 and y_diff < last[3] * 0.5:
            # Merge: create bounding box around both
            x1 = min(last[0], current[0])
            y1 = min(last[1], current[1])
            x2 = max(last[0] + last[2], current[0] + current[2])
            y2 = max(last[1] + last[3], current[1] + current[3])
            merged[-1] = [x1, y1, x2 - x1, y2 - y1]
        else:
            merged.append(current)
    
    return merged

def process_image_end_to_end(binary, original_debug=None):
    """
    Orchestrates Steps 4-6 and returns structured data.
    """
    from sklearn.cluster import KMeans

    lines_bboxes = detect_lines(binary, original_debug)
    structured_output = []
    
    for (lx, ly, lw, lh) in lines_bboxes:
        line_binary = binary[ly:ly+lh, lx:lx+lw]
        char_bboxes = segment_chars_from_line(line_binary)
        
        if not char_bboxes:
            continue
            
        # Step 8: Word Reconstruction (Gap Analysis)
        # 1. Collect all gaps
        gaps = []
        # Re-calc bboxes with padding applied for gap logic
        real_boxes = []
        for (cx, cy, cw, ch, px, py) in char_bboxes:
             real_boxes.append((cx, cy, cw, ch))

        for i in range(len(real_boxes) - 1):
            curr_end = real_boxes[i][0] + real_boxes[i][2]
            next_start = real_boxes[i+1][0]
            gaps.append(max(0, next_start - curr_end))
            
        # 2. Cluster gaps
        space_threshold = 999
        if len(gaps) > 1:
            try:
                gaps_np = np.array(gaps).reshape(-1, 1)
                kmeans = KMeans(n_clusters=2, n_init=10, random_state=42).fit(gaps_np)
                centers = sorted(kmeans.cluster_centers_.flatten())
                space_threshold = (centers[0] + centers[1]) / 2
            except:
                avg_w = np.mean([b[2] for b in real_boxes])
                space_threshold = avg_w * 0.5
        elif real_boxes:
             avg_w = np.mean([b[2] for b in real_boxes])
             space_threshold = avg_w * 0.5

        line_chars = []
        h_line, w_line = line_binary.shape
        
        for i, (cx, cy, cw, ch, px, py) in enumerate(char_bboxes):
            # Apply padding safely
            x1 = max(0, cx - px)
            y1 = max(0, cy - py)
            x2 = min(w_line, cx + cw + px)
            y2 = min(h_line, cy + ch + py)
            
            char_roi = line_binary[y1:y2, x1:x2]
            
            # Draw char box on debug (Green)
            if original_debug is not None:
                gx, gy = lx + x1, ly + y1
                cv2.rectangle(original_debug, (gx, gy), (lx + x2, ly + y2), (0, 255, 0), 1)
            
            # Check for space after
            is_space = False
            if i < len(char_bboxes) - 1:
                curr_end = cx + cw
                next_start = char_bboxes[i+1][0]
                dist = next_start - curr_end
                if dist >= space_threshold:
                    is_space = True
                    
            line_chars.append({
                "img": char_roi,
                "space": is_space
            })
            
        structured_output.append(line_chars)
        
    return structured_output
