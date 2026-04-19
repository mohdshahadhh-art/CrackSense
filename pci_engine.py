# pci_engine.py
# PCI Scoring Engine based on ASTM D6433

# Deduct values per damage type and severity
DEDUCT_VALUES = {
    'longitudinal_crack': {'low': 5,  'medium': 13, 'high': 20},
    'transverse_crack':   {'low': 5,  'medium': 13, 'high': 20},
    'alligator_crack':    {'low': 15, 'medium': 30, 'high': 45},
    'pothole':            {'low': 25, 'medium': 45, 'high': 65},
    'other_damage':       {'low': 5,  'medium': 10, 'high': 15},
}

# Official ASTM D6433 PCI rating scale + colors
PCI_RATINGS = [
    (85, 100, 'Good',         '#1a7a1a'),  # Dark Green
    (70,  85, 'Satisfactory', '#5cb85c'),  # Light Green
    (55,  70, 'Fair',         '#f0ad4e'),  # Yellow
    (40,  55, 'Poor',         '#e8735a'),  # Light Red
    (25,  40, 'Very Poor',    '#c0392b'),  # Medium Red
    (10,  25, 'Serious',      '#7b241c'),  # Dark Red
    ( 0,  10, 'Failed',       '#424242'),  # Dark Grey
]

CLASS_NAMES = [
    'longitudinal_crack',
    'transverse_crack',
    'alligator_crack',
    'pothole',
    'other_damage'
]

def get_severity(box_area_ratio):
    """Estimate severity from bounding box size relative to image."""
    if box_area_ratio < 0.05:
        return 'low'
    elif box_area_ratio < 0.15:
        return 'medium'
    else:
        return 'high'

def get_pci_rating(score):
    """Return rating label and color for a given PCI score."""
    for low, high, label, color in PCI_RATINGS:
        if low <= score <= high:
            return label, color
    return 'Failed', '#424242'

def calculate_pci(detections, img_width, img_height):
    """
    Calculate PCI score from YOLO detections.
    
    detections: list of (class_id, confidence, x1, y1, x2, y2)
    img_width, img_height: image dimensions
    
    Returns: dict with score, rating, color, and damage details
    """
    img_area = img_width * img_height
    total_deduct = 0
    damage_details = []

    for class_id, confidence, x1, y1, x2, y2 in detections:
        damage_type = CLASS_NAMES[int(class_id)]
        
        # Calculate how much of the image this damage covers
        box_area = (x2 - x1) * (y2 - y1)
        box_area_ratio = box_area / img_area
        
        # Get severity and deduct value
        severity = get_severity(box_area_ratio)
        deduct = DEDUCT_VALUES[damage_type][severity]
        total_deduct += deduct
        
        damage_details.append({
            'type': damage_type,
            'severity': severity,
            'confidence': round(confidence, 2),
            'deduct': deduct
        })

    # PCI cannot go below 0
    pci_score = max(0, 100 - total_deduct)
    rating, color = get_pci_rating(pci_score)

    return {
        'pci_score': round(pci_score, 1),
        'rating': rating,
        'color': color,
        'total_deduct': total_deduct,
        'damages': damage_details
    }


# ── Quick test ──────────────────────────────────────────────
if __name__ == '__main__':
    # Simulate what YOLO would detect on a bad road
    fake_detections = [
        (3, 0.91, 100, 200, 300, 350),   # pothole, medium size
        (2, 0.78, 50,  100, 400, 500),   # alligator crack, large
        (0, 0.65, 10,  10,  80,  30),    # longitudinal crack, small
    ]

    result = calculate_pci(fake_detections, img_width=640, img_height=640)

    print(f"\n{'='*40}")
    print(f"  PCI Score : {result['pci_score']} / 100")
    print(f"  Rating    : {result['rating']}")
    print(f"  Color     : {result['color']}")
    print(f"{'='*40}")
    print(f"\nDamage breakdown:")
    for d in result['damages']:
        print(f"  - {d['type']} ({d['severity']} severity) "
              f"→ deduct {d['deduct']} pts  [conf: {d['confidence']}]")
    print(f"\n  Total deducted: {result['total_deduct']} pts")
    print(f"  Final PCI: 100 - {result['total_deduct']} = {result['pci_score']}")