import os
import time
import hashlib
import secrets
import smtplib
from email.message import EmailMessage

import pandas as pd
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

try:
    from streamlit_geolocation import streamlit_geolocation
except Exception:
    streamlit_geolocation = None

from db import (
    create_table,
    add_pothole,
    get_all_potholes,
    get_report_by_id,
    update_status,
    update_ai_result,
    add_alert,
    get_alerts,
    mark_alert_read,
)
from scoring import calculate_priority
from ai_detector import analyze_image

st.set_page_config(
    page_title="RoadPulse",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

create_table()
os.makedirs("uploads", exist_ok=True)

# -------------------- STYLE --------------------
st.markdown("""
<style>
/* =========================================================
   ROADPULSE DARK THEME
   FUNCTIONALITY IS NOT CHANGED
   ========================================================= */

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(59,130,246,0.14), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(139,92,246,0.12), transparent 30%),
        linear-gradient(135deg, #080d18 0%, #0b1220 50%, #0f172a 100%);
    color: #f1f5f9 !important;
}

/* Main page */
.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* =========================================================
   ALL NORMAL TEXT
   ========================================================= */

.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp div,
.stApp li {
    color: #e5e7eb;
}

h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
}

/* Markdown text */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {
    color: #e2e8f0 !important;
}

/* =========================================================
   HERO SECTION
   ========================================================= */

.hero {
    background: linear-gradient(
        135deg,
        #172554 0%,
        #312e81 48%,
        #0e7490 100%
    );

    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 26px;
    padding: 38px 42px;
    margin-bottom: 25px;

    box-shadow:
        0 20px 50px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.08);
}

.hero h1,
.hero h2,
.hero h3,
.hero p,
.hero span {
    color: #ffffff !important;
}

/* =========================================================
   NAVIGATION / BUTTONS
   ========================================================= */

div.stButton > button {
    background: #172033 !important;
    color: #f8fafc !important;

    border: 1px solid #334155 !important;
    border-radius: 13px !important;

    min-height: 48px;

    font-size: 15px;
    font-weight: 700;

    box-shadow: 0 5px 18px rgba(0,0,0,0.25);

    transition: 0.2s ease;
}

/* NORMAL STATE — text is already visible */
div.stButton > button p {
    color: #f8fafc !important;
}

div.stButton > button span {
    color: #f8fafc !important;
}

/* HOVER — still visible */
div.stButton > button:hover {
    background: #253352 !important;
    color: #ffffff !important;
    border-color: #60a5fa !important;
    box-shadow: 0 8px 24px rgba(59,130,246,0.20);
}

div.stButton > button:hover p,
div.stButton > button:hover span {
    color: #ffffff !important;
}

/* CLICKED */
div.stButton > button:focus,
div.stButton > button:active {
    color: #ffffff !important;
    background: #1e3a5f !important;
    border-color: #60a5fa !important;
}

/* =========================================================
   FEATURE CARDS
   ========================================================= */

.info-card {
    background: #111827;
    border: 1px solid #263449;

    border-radius: 20px;
    padding: 24px;

    min-height: 195px;

    box-shadow: 0 12px 30px rgba(0,0,0,0.28);
}

.info-card:hover {
    background: #162033;
    border-color: #3b82f6;
}

.info-card .icon {
    font-size: 40px;
    margin-bottom: 12px;
}

.info-card h3 {
    color: #93c5fd !important;
    font-size: 20px;
    font-weight: 800;
}

.info-card p {
    color: #cbd5e1 !important;
    line-height: 1.6;
}

/* =========================================================
   SECTION TITLES
   ========================================================= */

.section-title {
    color: #f8fafc !important;
    font-size: 30px;
    font-weight: 850;
    margin: 32px 0 17px;
}

/* =========================================================
   TEXT INPUTS
   ========================================================= */

div[data-baseweb="input"] {
    background: #111827 !important;
    border-radius: 10px !important;
}

div[data-baseweb="input"] > div {
    background: #111827 !important;
    border: 1px solid #334155 !important;
}

div[data-baseweb="input"] input {
    color: #f8fafc !important;
    background: #111827 !important;
    caret-color: #60a5fa !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #94a3b8 !important;
}

/* =========================================================
   TEXT AREA
   ========================================================= */

textarea {
    color: #f8fafc !important;
    background: #111827 !important;
    border: 1px solid #334155 !important;
}

textarea::placeholder {
    color: #94a3b8 !important;
}

/* =========================================================
   DROPDOWN / SELECTBOX
   ========================================================= */

div[data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid #334155 !important;
}

div[data-baseweb="select"] span {
    color: #f8fafc !important;
}

div[data-baseweb="select"] input {
    color: #f8fafc !important;
}

/* Dropdown menu */
ul[role="listbox"] {
    background: #111827 !important;
    border: 1px solid #334155 !important;
}

li[role="option"] {
    color: #f8fafc !important;
    background: #111827 !important;
}

li[role="option"]:hover {
    color: #ffffff !important;
    background: #1e3a5f !important;
}

/* =========================================================
   RADIO BUTTONS
   ========================================================= */

div[role="radiogroup"] label {
    color: #e5e7eb !important;
}

div[role="radiogroup"] label p {
    color: #e5e7eb !important;
}

/* =========================================================
   CHECKBOXES
   ========================================================= */

[data-testid="stCheckbox"] label {
    color: #e5e7eb !important;
}

[data-testid="stCheckbox"] label p {
    color: #e5e7eb !important;
}

/* =========================================================
   SLIDER
   ========================================================= */

[data-testid="stSlider"] label,
[data-testid="stSlider"] p {
    color: #e5e7eb !important;
}

/* =========================================================
   FILE UPLOADER
   ========================================================= */

[data-testid="stFileUploader"] {
    background: #111827 !important;
    border: 1px solid #334155 !important;
    border-radius: 14px !important;
}

[data-testid="stFileUploader"] section {
    background: #111827 !important;
}

[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small {
    color: #cbd5e1 !important;
}

/* =========================================================
   METRICS
   ========================================================= */

[data-testid="stMetric"] {
    background: #111827 !important;
    border: 1px solid #263449 !important;
    border-radius: 16px;

    padding: 18px;

    box-shadow: 0 10px 28px rgba(0,0,0,0.25);
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
}

[data-testid="stMetricDelta"] {
    color: #93c5fd !important;
}

/* =========================================================
   EXPANDERS
   ========================================================= */

[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #263449 !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] summary {
    color: #f8fafc !important;
}

[data-testid="stExpander"] summary span {
    color: #f8fafc !important;
}

/* =========================================================
   ALERT / INFO BOXES
   ========================================================= */

[data-testid="stAlert"] {
    background: #172033 !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
}

[data-testid="stAlert"] p {
    color: #e2e8f0 !important;
}

/* =========================================================
   DATAFRAME / TABLE
   ========================================================= */

[data-testid="stDataFrame"] {
    border: 1px solid #334155 !important;
}

[data-testid="stDataFrame"] * {
    color: #e5e7eb !important;
}

/* =========================================================
   CODE BLOCKS
   ========================================================= */

code {
    background: #020617 !important;
    color: #93c5fd !important;
}

/* =========================================================
   LINKS
   ========================================================= */

a {
    color: #93c5fd !important;
}

a:hover {
    color: #bfdbfe !important;
}

/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #080d18 0%,
        #111827 55%,
        #172033 100%
    );
    border-right: 1px solid #263449;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #e5e7eb !important;
}

/* =========================================================
   REPORT ID
   ========================================================= */

.report-id {
    color: #93c5fd !important;
    font-size: 30px;
    font-weight: 900;
}

/* =========================================================
   STATUS COLORS
   ========================================================= */

.status-high {
    color: #f87171 !important;
    font-weight: 850;
}

.status-medium {
    color: #fbbf24 !important;
    font-weight: 850;
}

.status-low {
    color: #4ade80 !important;
    font-weight: 850;
}

/* =========================================================
   NOTICE
   ========================================================= */

.notice {
    background: #172033 !important;
    border-left: 5px solid #60a5fa;

    border-radius: 12px;
    padding: 14px 17px;

    color: #e2e8f0 !important;
}

/* =========================================================
   SUCCESS BOX
   ========================================================= */

.success-box {
    background: #052e1b !important;
    border: 1px solid #166534;

    border-radius: 14px;
    padding: 18px;

    color: #bbf7d0 !important;
}

.success-box * {
    color: #bbf7d0 !important;
}

/* =========================================================
   DIVIDERS
   ========================================================= */

hr {
    border-color: #263449 !important;
}

/* =========================================================
   STREAMLIT TOP HEADER
   ========================================================= */

[data-testid="stHeader"] {
    background: #080d18 !important;
}

/* =========================================================
   DOWNLOAD BUTTON
   ========================================================= */

[data-testid="stDownloadButton"] button {
    background: #172033 !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
}

[data-testid="stDownloadButton"] button span,
[data-testid="stDownloadButton"] button p {
    color: #f8fafc !important;
}

/* =========================================================
   SPINNER / STATUS TEXT
   ========================================================= */

[data-testid="stSpinner"] {
    color: #e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION --------------------
def init_session():
    defaults = {
        "page": "home",
        "gov_authenticated": False,
        "gov_email": "",
        "otp_hash": "",
        "otp_created": 0.0,
        "otp_email": "",
        "last_report_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# -------------------- HELPERS --------------------
def go(page):
    st.session_state.page = page
    st.rerun()


def get_allowed_domains():
    try:
        configured = st.secrets.get("ALLOWED_GOV_EMAIL_DOMAINS", None)
    except Exception:
        configured = None
    if configured:
        if isinstance(configured, str):
            domains = [x.strip().lower().lstrip("@") for x in configured.split(",")]
        else:
            domains = [str(x).strip().lower().lstrip("@") for x in configured]
        return [d for d in domains if d]
    return ["gov.in", "nic.in"]


def is_official_gov_email(email):
    email = email.strip().lower()
    if "@" not in email:
        return False
    domain = email.rsplit("@", 1)[1]
    return any(domain == allowed or domain.endswith("." + allowed) for allowed in get_allowed_domains())


def send_otp_email(recipient, otp):
    try:
        host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        port = int(st.secrets.get("SMTP_PORT", 587))
        sender = st.secrets.get("SMTP_EMAIL", "")
        password = st.secrets.get("SMTP_PASSWORD", "")
        if not sender or not password:
            return False, "SMTP credentials are not configured."
        msg = EmailMessage()
        msg["Subject"] = "RoadPulse Government Portal OTP"
        msg["From"] = sender
        msg["To"] = recipient
        msg.set_content(f"Your RoadPulse verification OTP is: {otp}\n\nThis OTP expires in 5 minutes.")
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        return True, "OTP sent to the official email address."
    except Exception as exc:
        return False, str(exc)


def priority_badge(level):
    level = str(level or "Low")
    if level == "High":
        return "🔴 High"
    if level == "Medium":
        return "🟠 Medium"
    return "🟢 Low"


def location_from_widget():
    if streamlit_geolocation is None:
        return None
    try:
        return streamlit_geolocation()
    except Exception:
        return None


def reverse_geocode(lat, lon):
    """Return a human-readable area/address when the internet geocoder is available."""
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "zoom": 18,
                "addressdetails": 1,
            },
            headers={"User-Agent": "RoadPulse-College-Project/1.0"},
            timeout=8,
        )
        if response.ok:
            data = response.json()
            return data.get("display_name", "")
    except Exception:
        pass
    return ""


def show_location_map(lat, lon, title="Reported Pothole Location"):
    """Show the GPS point on a normal map so users do not have to interpret coordinates."""
    fmap = folium.Map(
        location=[float(lat), float(lon)],
        zoom_start=17,
        control_scale=True,
        tiles="OpenStreetMap",
    )
    folium.Marker(
        [float(lat), float(lon)],
        tooltip="📍 Pothole location",
        popup=title,
        icon=folium.Icon(color="red", icon="warning-sign"),
    ).add_to(fmap)
    folium.Circle(
        [float(lat), float(lon)],
        radius=35,
        color="#e63946",
        fill=True,
        fill_opacity=0.18,
    ).add_to(fmap)
    st_folium(fmap, width=None, height=380, returned_objects=[])

# -------------------- TOP NAV --------------------
st.markdown("## 🛣️ RoadPulse")
nav = st.columns(4)
with nav[0]:
    if st.button("🏠 Home", use_container_width=True, key="nav_home"): go("home")
with nav[1]:
    if st.button("🚨 Report a Pothole", use_container_width=True, key="nav_report"): go("report")
with nav[2]:
    if st.button("🔎 Track My Report", use_container_width=True, key="nav_track"): go("track")
with nav[3]:
    if st.button("🏛️ Government Portal", use_container_width=True, key="nav_government"): go("government")

# -------------------- HOME --------------------
def home_page():
    st.markdown("""
    <div class="hero">
        <h1>🛣️ RoadPulse</h1>
        <p><b>Smarter Roads. Safer Journeys.</b></p>
        <p>Report potholes, capture their location, analyze severity and help road authorities organize repairs.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🚨 Report a Pothole", use_container_width=True, type="primary", key="home_report"):
            go("report")
    with c2:
        if st.button("🔎 Track My Report", use_container_width=True, key="home_track"):
            go("track")
    with c3:
        if st.button("🏛️ Government Portal", use_container_width=True, key="home_government"):
            go("government")

    st.markdown('<div class="section-title">How RoadPulse Works</div>', unsafe_allow_html=True)
    cards = [
        ("📷", "Report Easily", "Upload a pothole photo and enter the basic road and location details."),
        ("📍", "Capture Location", "Use GPS location to record where the pothole was reported."),
        ("🤖", "AI Analysis", "The optional AI model analyzes the uploaded image and provides a prototype severity result."),
        ("🚦", "Priority Scoring", "The system combines size, depth, traffic, road type, urgency and other factors to calculate priority."),
        ("🏛️", "Government Action", "Authorized officials can view reports, priorities, alerts and repair progress."),
        ("🔎", "Track Your Report", "Every submission receives a unique Report ID. Use that ID to check its current status."),
    ]
    for start in range(0, len(cards), 3):
        cols = st.columns(3)
        for col, (icon, title, text) in zip(cols, cards[start:start + 3]):
            with col:
                st.markdown(
                    f'<div class="info-card"><div class="icon">{icon}</div><h3>{title}</h3><p>{text}</p></div>',
                    unsafe_allow_html=True,
                )
        st.write("")

    st.markdown('<div class="section-title">Why RoadPulse?</div>', unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    a.metric("📌 Report", "Simple")
    b.metric("📍 Location", "GPS")
    c.metric("🤖 Analysis", "AI-ready")
    d.metric("⚡ Priority", "Automatic")

# -------------------- REPORT --------------------
def report_page():
    st.markdown("## 🚨 Report a Pothole")
    st.markdown('<div class="notice"><b>Important:</b> Your phone number or email is optional and is not used to track your report. Your unique Report ID is used for tracking.</div>', unsafe_allow_html=True)

    location = location_from_widget()
    lat = None
    lon = None
    if location:
        lat = location.get("latitude")
        lon = location.get("longitude")
        if lat is not None and lon is not None:
            lat = float(lat)
            lon = float(lon)
            st.success("📍 GPS location captured successfully.")
            st.markdown("**Check the red pin on the map below. It shows the location your phone/browser reported.**")
            address = reverse_geocode(lat, lon)
            if address:
                st.info(f"📌 Approximate location: {address}")
            else:
                st.info("📌 The map confirms the location. A readable address could not be loaded right now.")
            show_location_map(lat, lon, "Pothole reported here")
        else:
            st.warning("GPS permission is available, but a location has not been returned yet. Allow browser location access and try again.")
    else:
        st.info("GPS widget is unavailable. Please allow location access in the browser and try again.")

    with st.form("pothole_report_form", clear_on_submit=False):
        left, right = st.columns(2)
        with left:
            name = st.text_input("Name (optional)")
            contact = st.text_input("Phone / Email (optional)")
            ward = st.text_input("City Ward *")
            road = st.text_input("Road / Street Name *")
            landmark = st.text_input("Nearby Landmark")
            road_type = st.selectbox("Road Type", ["Residential", "Main Road", "Highway", "School Zone", "Hospital Area", "Market Area"])
            road_usage = st.selectbox("Road Usage", ["Low", "Medium", "High"])
        with right:
            size = st.selectbox("Pothole Size", ["Small", "Medium", "Large"])
            depth = st.selectbox("Pothole Depth", ["Shallow", "Moderate", "Deep"])
            pothole_count = st.selectbox("Number of Potholes", ["1", "2-5", "More than 5"])
            traffic_problem = st.selectbox("Traffic Problem", ["No", "Sometimes", "Yes"])
            accident_reported = st.selectbox("Accident Reported", ["No", "Not Sure", "Yes"])
            urgency = st.slider("Urgency", 1, 5, 3)
            water_filled = st.selectbox("Water Filled / Water Logging", ["No", "Yes"])

        image = st.file_uploader("Pothole Photo *", type=["jpg", "jpeg", "png"])
        remarks = st.text_area("Additional Remarks")
        submitted = st.form_submit_button("🚀 Submit Pothole Report", type="primary", use_container_width=True)

    if submitted:
        if not ward.strip():
            st.error("Please enter the City Ward.")
            return
        if not road.strip():
            st.error("Please enter the Road / Street Name.")
            return
        if image is None:
            st.error("Please upload a pothole photo.")
            return
        if lat is None or lon is None:
            st.error("GPS location is required. Allow browser location access and click the GPS widget again.")
            return

        score, priority = calculate_priority(
            size=size,
            depth=depth,
            road_type=road_type,
            traffic_problem=traffic_problem,
            accident_reported=accident_reported,
            pothole_count=pothole_count,
            water_filled=water_filled,
            urgency=urgency,
        )

        ext = os.path.splitext(image.name)[1].lower() or ".jpg"
        safe_name = f"report_{int(time.time())}_{secrets.token_hex(4)}{ext}"
        image_path = os.path.join("uploads", safe_name)
        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

        report_id = add_pothole(
            name=name.strip(), contact=contact.strip(), citizen_username="",
            ward=ward.strip(), road=road.strip(), landmark=landmark.strip(),
            latitude=float(lat), longitude=float(lon), image_path=image_path,
            size=size, depth=depth, pothole_count=pothole_count,
            road_type=road_type, traffic_problem=traffic_problem,
            accident_reported=accident_reported, urgency=urgency,
            road_usage=road_usage, water_filled=water_filled,
            remarks=remarks.strip(), priority_score=score, priority_level=priority,
            status="Pending",
        )

        result, confidence, ai_severity = analyze_image(image_path)
        update_ai_result(report_id, result, confidence, ai_severity)
        add_alert(report_id, "New Report", f"New {priority} priority pothole report #{report_id} received.", priority)
        st.session_state.last_report_id = report_id

        st.markdown(f"""
        <div class="success-box">
            <div>✅ Your pothole report has been submitted successfully.</div>
            <div class="report-id">Report ID: #{report_id}</div>
            <div><b>Priority:</b> {priority_badge(priority)} &nbsp; | &nbsp; <b>Score:</b> {score}</div>
            <div><b>AI result:</b> {ai_severity} ({confidence:.1f}% confidence)</div>
            <div style="margin-top:8px">Save your Report ID. You need this ID to track the report later.</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔎 Track This Report", key="track_map_report"):
            go("track")

# -------------------- TRACK --------------------
def track_page():
    st.markdown("## 🔎 Track My Report")
    st.write("Enter the unique Report ID you received after submitting the pothole report.")
    report_id_text = st.text_input("Report ID", placeholder="Example: 12")
    if st.button("🔍 Find Report", type="primary", key="find_report"):
        clean_id = report_id_text.strip().lstrip("#")
        if not clean_id.isdigit():
            st.error("Please enter a valid numeric Report ID, such as 12 or #12.")
            return
        report = get_report_by_id(int(clean_id))
        if not report:
            st.error("No report was found with that Report ID.")
            return

        st.success(f"Report #{report['id']} found.")
        a, b, c = st.columns(3)
        a.metric("Priority", report["priority_level"])
        b.metric("Priority Score", report["priority_score"])
        c.metric("Repair Status", report["status"])
        st.write(f"**Ward:** {report['ward']}")
        st.write(f"**Road:** {report['road']}")
        st.markdown("### 📍 Reported Location")
        address = reverse_geocode(float(report['latitude']), float(report['longitude']))
        if address:
            st.info(f"📌 Approximate location: {address}")
        else:
            st.info("The red pin below shows the GPS location captured with this report.")
        show_location_map(float(report['latitude']), float(report['longitude']), f"Report #{report['id']}")
        st.write(f"**Submitted:** {report['created_at']}")
        st.write(f"**AI Severity:** {report['ai_severity'] or 'Not Analyzed'}")
        if report.get("ai_result"):
            st.write(f"**AI Result:** {report['ai_result']} ({float(report.get('ai_confidence') or 0):.1f}%)")

# -------------------- GOVERNMENT --------------------
def government_login():
    st.markdown("## 🏛️ Government Portal")
    st.markdown(f'<div class="notice"><b>Official email domains accepted:</b> {", ".join("@" + d for d in get_allowed_domains())}</div>', unsafe_allow_html=True)
    email = st.text_input("Official Government Email", placeholder="name@department.gov.in")

    if st.button("📩 Send OTP", type="primary", key="send_otp"):
        if not is_official_gov_email(email):
            st.error("Please enter an official government email address using an allowed domain.")
        else:
            otp = f"{secrets.randbelow(1000000):06d}"
            st.session_state.otp_hash = hashlib.sha256(otp.encode()).hexdigest()
            st.session_state.otp_created = time.time()
            st.session_state.otp_email = email.strip().lower()
            sent, message = send_otp_email(st.session_state.otp_email, otp)
            if sent:
                st.success(message)
            else:
                # Local college-project fallback so the portal can be demonstrated without SMTP.
                st.warning("SMTP is not configured. Demo mode is active for local testing.")
                st.info("For this local demo only, your OTP is shown below.")
                st.code(otp)

    if st.session_state.otp_hash:
        st.divider()
        st.write(f"OTP sent/requested for: **{st.session_state.otp_email}**")
        otp_input = st.text_input("Enter 6-digit OTP", max_chars=6)
        if st.button("✅ Verify OTP", key="verify_otp"):
            if time.time() - st.session_state.otp_created > 300:
                st.error("OTP expired. Please request a new OTP.")
            elif hashlib.sha256(otp_input.strip().encode()).hexdigest() != st.session_state.otp_hash:
                st.error("Incorrect OTP.")
            else:
                st.session_state.gov_authenticated = True
                st.session_state.gov_email = st.session_state.otp_email
                st.session_state.otp_hash = ""
                st.success("Government portal login successful.")
                st.rerun()


def government_dashboard():
    st.markdown("## 🏛️ Government Dashboard")
    top1, top2, top3 = st.columns([5, 1, 1])
    with top1:
        st.write(f"Signed in as **{st.session_state.gov_email}**")
    with top2:
        if st.button("🔄 Refresh", key="gov_refresh"):
            st.rerun()
    with top3:
        if st.button("Logout", key="gov_logout"):
            st.session_state.gov_authenticated = False
            st.session_state.gov_email = ""
            go("government")

    df = get_all_potholes()
    alerts = get_alerts()
    unread = sum(1 for a in alerts if not a["is_read"])

    total = len(df)
    high = int((df["priority_level"] == "High").sum()) if total else 0
    medium = int((df["priority_level"] == "Medium").sum()) if total else 0
    low = int((df["priority_level"] == "Low").sum()) if total else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Reports", total)
    m2.metric("🔴 High", high)
    m3.metric("🟠 Medium", medium)
    m4.metric("🟢 Low", low)
    m5.metric("🔔 Unread Alerts", unread)

    st.markdown("### 🔔 Alerts")
    if alerts:
        for alert in alerts[:15]:
            col1, col2 = st.columns([5, 1])
            with col1:
                read_text = "Read" if alert["is_read"] else "NEW"
                st.write(f"**{read_text}** — Report #{alert['pothole_id']}: {alert['message']}")
            with col2:
                if not alert["is_read"] and st.button("Mark read", key=f"read_{alert['id']}"):
                    mark_alert_read(alert["id"])
                    st.rerun()
    else:
        st.info("No alerts yet.")

    st.markdown("### 📋 Reports & Repair Tracking")
    if total:
        display = df[["id", "ward", "road", "priority_score", "priority_level", "status", "ai_severity", "created_at"]].copy()
        st.dataframe(display, use_container_width=True, hide_index=True)

        report_options = [int(x) for x in df["id"].tolist()]
        selected_id = st.selectbox("Select a report to manage", report_options)
        selected = df[df["id"] == selected_id].iloc[0]

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Report #{selected_id}**")
            st.write(f"Ward: {selected['ward']}")
            st.write(f"Road: {selected['road']}")
            st.write(f"Priority: {priority_badge(selected['priority_level'])}")
            st.write(f"AI severity: {selected['ai_severity'] or 'Not Analyzed'}")
        with c2:
            new_status = st.selectbox(
                "Repair Status",
                ["Pending", "Under Review", "Repair Assigned", "In Progress", "Repaired"],
                index=["Pending", "Under Review", "Repair Assigned", "In Progress", "Repaired"].index(selected["status"] if selected["status"] in ["Pending", "Under Review", "Repair Assigned", "In Progress", "Repaired"] else "Pending"),
            )
            if st.button("💾 Update Repair Status", key="update_repair_status"):
                update_status(selected_id, new_status)
                st.success("Repair status updated.")
                st.rerun()

        st.markdown("### 🤖 AI Analysis")
        if selected["image_path"] and os.path.exists(selected["image_path"]):
            st.image(selected["image_path"], width=420)
            if st.button("Analyze Selected Photo Again", key="analyze_selected_photo"):
                result, confidence, severity = analyze_image(selected["image_path"])
                update_ai_result(selected_id, result, confidence, severity)
                st.success(f"AI result: {result} | Severity: {severity} | Confidence: {confidence:.1f}%")
                st.rerun()
        else:
            st.info("The uploaded image file is not available.")

        st.markdown("### 📍 Priority Map")
        map_df = df.dropna(subset=["latitude", "longitude"])
        if not map_df.empty:
            center = [float(map_df["latitude"].mean()), float(map_df["longitude"].mean())]
            fmap = folium.Map(location=center, zoom_start=13, control_scale=True, tiles="OpenStreetMap")
            for _, row in map_df.iterrows():
                level = str(row["priority_level"])
                icon_color = "red" if level == "High" else "orange" if level == "Medium" else "green"
                popup = (
                    f"<b>Report #{row['id']}</b><br>"
                    f"Priority: {level}<br>"
                    f"Status: {row['status']}<br>"
                    f"Road: {row['road']}<br>"
                    f"Ward: {row['ward']}"
                )
                folium.Marker(
                    [float(row["latitude"]), float(row["longitude"])],
                    popup=folium.Popup(popup, max_width=300),
                    tooltip=f"Report #{row['id']} - {level}",
                    icon=folium.Icon(color=icon_color, icon="warning-sign"),
                ).add_to(fmap)
            st.markdown("**Map legend:** 🔴 High priority &nbsp;&nbsp; 🟠 Medium priority &nbsp;&nbsp; 🟢 Low priority")
            st_folium(fmap, width=None, height=480, returned_objects=[])

        st.markdown("### 📊 Analytics")
        chart_data = pd.DataFrame({
            "Priority": ["High", "Medium", "Low"],
            "Reports": [high, medium, low],
        }).set_index("Priority")
        st.bar_chart(chart_data)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Reports CSV", csv_data, "roadpulse_reports.csv", "text/csv")
    else:
        st.info("No pothole reports have been submitted yet.")

# -------------------- ROUTER --------------------
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "report":
    report_page()
elif st.session_state.page == "track":
    track_page()
elif st.session_state.page == "government":
    if st.session_state.gov_authenticated:
        government_dashboard()
    else:
        government_login()
