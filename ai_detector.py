import os


def analyze_image(image_path):
    model_path = os.path.join("models", "best.pt")
    if not os.path.exists(model_path):
        return "AI model not installed", 0.0, "Not Analyzed"

    try:
        from ultralytics import YOLO
        from PIL import Image

        model = YOLO(model_path)
        results = model.predict(source=image_path, verbose=False)
        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            return "No pothole detected", 0.0, "Low"

        result = results[0]
        boxes = result.boxes
        confs = boxes.conf.cpu().numpy().tolist()
        best_index = max(range(len(confs)), key=lambda i: confs[i])
        confidence = float(confs[best_index]) * 100.0

        image = Image.open(image_path)
        width, height = image.size
        image_area = max(width * height, 1)
        xyxy = boxes.xyxy[best_index].cpu().numpy().tolist()
        x1, y1, x2, y2 = xyxy
        box_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        area_ratio = box_area / image_area

        if area_ratio >= 0.25:
            severity = "High"
        elif area_ratio >= 0.10:
            severity = "Medium"
        else:
            severity = "Low"

        return "Pothole detected", confidence, severity
    except Exception as exc:
        return f"AI analysis error: {type(exc).__name__}", 0.0, "Not Analyzed"
