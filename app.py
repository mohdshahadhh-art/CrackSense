import streamlit as st
from ultralytics import YOLO
from pci_engine import calculate_pci
from report import generate_report
from PIL import Image
import folium
from streamlit_folium import st_folium
import tempfile, os

st.set_page_config(
    page_title="CrackSense",
    page_icon="🛣️",
    layout="wide"
)

@st.cache_resource
def load_model():
    return YOLO("C:/CrackSense/runs/cracksense_v1/weights/best.pt")

model = load_model()

st.title("🛣️ CrackSense")
st.caption("AI-powered road damage detection & PCI scoring system")
st.divider()

with st.sidebar:
    st.header("Settings")
    confidence = st.slider("Detection confidence", 0.1, 0.9, 0.25)
    st.divider()
    st.markdown("**Damage Classes**")
    st.markdown("🔴 Pothole")
    st.markdown("🟠 Alligator crack")
    st.markdown("🟡 Longitudinal crack")
    st.markdown("🟢 Transverse crack")
    st.divider()
    st.markdown("**PCI Scale (ASTM D6433)**")
    st.markdown("🟢 85-100 Good")
    st.markdown("🟢 70-85 Satisfactory")
    st.markdown("🟡 55-70 Fair")
    st.markdown("🟠 40-55 Poor")
    st.markdown("🔴 25-40 Very Poor")
    st.markdown("🔴 10-25 Serious")
    st.markdown("⚫ 0-10 Failed")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Road Image")
    uploaded = st.file_uploader(
        "Choose a road image",
        type=["jpg", "jpeg", "png"]
    )
    st.subheader("Location (optional)")
    lat = st.number_input("Latitude",  value=10.8505)
    lon = st.number_input("Longitude", value=76.2711)

if uploaded is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
        f.write(uploaded.read())
        tmp_path = f.name

    with st.spinner("Detecting road damage..."):
        results   = model(tmp_path, conf=confidence)
        result_img = results[0].plot()
        img = Image.open(tmp_path)
        w, h = img.size

    detections = []
    for box in results[0].boxes:
        cls      = int(box.cls)
        conf_val = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        detections.append((cls, conf_val, x1, y1, x2, y2))

    pci_result = calculate_pci(detections, w, h)
    score  = pci_result['pci_score']
    rating = pci_result['rating']
    color  = pci_result['color']

    with col1:
        st.subheader("Detection Result")
        st.image(result_img, channels="BGR", width=500)

    with col2:
        st.subheader("PCI Score")
        st.markdown(
            f"""
            <div style='text-align:center; padding:20px;
                        background-color:{color}22;
                        border-radius:12px;
                        border: 2px solid {color}'>
                <h1 style='color:{color}; font-size:72px; margin:0'>{score}</h1>
                <h3 style='color:{color}; margin:0'>out of 100</h3>
                <h2 style='margin:8px 0'>{rating}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()
        st.subheader("Damage Breakdown")
        if detections:
            for d in pci_result['damages']:
                st.markdown(
                    f"**{d['type'].replace('_',' ').title()}** - "
                    f"{d['severity'].title()} severity - "
                    f"Deduct: {d['deduct']} pts - "
                    f"Confidence: {d['confidence']}"
                )
        else:
            st.success("No damage detected! Road is in good condition.")

        st.divider()
        st.subheader("Location Map")
        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.CircleMarker(
            location=[lat, lon],
            radius=15,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=f"PCI: {score} - {rating}"
        ).add_to(m)
        st_folium(m, height=300, width=None)

        st.divider()

        # PDF Download button
        st.subheader("Download Report")
        pdf_path = tempfile.mktemp(suffix=".pdf")

        with st.spinner("Generating PDF report..."):
            generate_report(
                result_img_bgr=result_img,
                pci_result=pci_result,
                lat=lat,
                lon=lon,
                output_path=pdf_path
            )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f.read(),
                file_name=f"CrackSense_Report_PCI{score}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        try:
            os.unlink(pdf_path)
        except:
            pass

    try:
        os.unlink(tmp_path)
    except:
        pass

else:
    with col2:
        st.info("Upload a road image on the left to get started.")