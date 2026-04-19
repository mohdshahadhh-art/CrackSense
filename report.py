from fpdf import FPDF
from datetime import datetime
import cv2, tempfile, os

class CrackSenseReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(30, 30, 30)
        self.cell(0, 15, 'CrackSense Road Inspection Report', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f'Generated: {datetime.now().strftime("%d %B %Y, %I:%M %p")}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'CrackSense AI | ASTM D6433 Standard | Page {self.page_no()}', align='C')


def generate_report(result_img_bgr, pci_result, lat, lon, output_path="CrackSense_Report.pdf"):
    score        = pci_result['pci_score']
    rating       = pci_result['rating']
    damages      = pci_result['damages']
    total_deduct = pci_result['total_deduct']

    tmp_img = tempfile.mktemp(suffix=".jpg")
    cv2.imwrite(tmp_img, result_img_bgr)

    pdf = CrackSenseReport()
    pdf.add_page()

    # Section 1: Inspection Details
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '1. Inspection Details', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, f'GPS Location   : {lat:.4f} N, {lon:.4f} E', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Inspection Date: {datetime.now().strftime("%d %B %Y")}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Standard Used  : ASTM D6433 (Pavement Condition Index)', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # Section 2: PCI Score
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '2. PCI Score', new_x='LMARGIN', new_y='NEXT')

    color_map = {
        'Good':         (26,  122, 26),
        'Satisfactory': (92,  184, 92),
        'Fair':         (240, 173, 78),
        'Poor':         (232, 115, 90),
        'Very Poor':    (192, 57,  43),
        'Serious':      (123, 36,  28),
        'Failed':       (66,  66,  66),
    }
    r, g, b = color_map.get(rating, (100, 100, 100))

    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 36)
    pdf.cell(60, 20, str(score), align='C', fill=True)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(80, 20, f'/ 100  -  {rating}', align='L', fill=True, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # Section 3: Detection Image
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '3. Detection Result', new_x='LMARGIN', new_y='NEXT')
    pdf.image(tmp_img, x=10, w=130)
    pdf.ln(4)

    # Section 4: Damage Breakdown
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '4. Damage Breakdown', new_x='LMARGIN', new_y='NEXT')

    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(70, 9, 'Damage Type',  fill=True)
    pdf.cell(35, 9, 'Severity',     fill=True, align='C')
    pdf.cell(35, 9, 'Confidence',   fill=True, align='C')
    pdf.cell(35, 9, 'Deduct (pts)', fill=True, align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.set_font('Helvetica', '', 10)
    for i, d in enumerate(damages):
        fill = i % 2 == 0
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(70, 8, d['type'].replace('_', ' ').title(), fill=fill)
        pdf.cell(35, 8, d['severity'].title(),               fill=fill, align='C')
        pdf.cell(35, 8, str(d['confidence']),                fill=fill, align='C')
        pdf.cell(35, 8, str(d['deduct']),                    fill=fill, align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(140, 8, 'Total Deducted', fill=True)
    pdf.cell(35,  8, str(total_deduct), fill=True, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # Section 5: Recommendation
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '5. Repair Recommendation', new_x='LMARGIN', new_y='NEXT')

    recommendations = {
        'Good':         'No immediate action required. Schedule routine monitoring.',
        'Satisfactory': 'Minor maintenance recommended within 12 months.',
        'Fair':         'Preventive maintenance required within 6 months.',
        'Poor':         'Corrective maintenance required within 3 months.',
        'Very Poor':    'Urgent repair required. Schedule within 1 month.',
        'Serious':      'Immediate repair required. Road poses safety risk.',
        'Failed':       'CRITICAL: Road has failed. Emergency repair or closure required.',
    }

    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 8, recommendations.get(rating, 'Assessment required.'))

    pdf.output(output_path)

    try:
        os.unlink(tmp_img)
    except:
        pass

    return output_path


if __name__ == '__main__':
    import numpy as np
    dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
    dummy_pci = {
        'pci_score': 45,
        'rating': 'Poor',
        'color': '#e8735a',
        'total_deduct': 55,
        'damages': [
            {'type': 'pothole',            'severity': 'medium', 'confidence': 0.87, 'deduct': 45},
            {'type': 'longitudinal_crack', 'severity': 'low',    'confidence': 0.65, 'deduct': 5},
            {'type': 'transverse_crack',   'severity': 'low',    'confidence': 0.55, 'deduct': 5},
        ]
    }
    path = generate_report(dummy_img, dummy_pci, lat=10.8505, lon=76.2711)
    print(f"Report saved to: {path}")