# =====================================
# IMPORTS
# =====================================
import streamlit as st
import pandas as pd
import base64
import os

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="Vendor AI", layout="wide")

# =====================================
# HIDE DEFAULT UI
# =====================================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =====================================
# IMAGE LOADER
# =====================================
def get_base64_image(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

abfrl_logo = get_base64_image("ABFRL_LOGO.jpg")
pantaloons_logo = get_base64_image("PANTALOONS_LOGO.png")


# =====================================
# CSS FIXED VERSION
# =====================================

st.markdown(f"""
<style>

/* FULL PAGE */
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, #0f9b8e, #003f3f);
}}

/* REMOVE EXTRA PADDING */
.block-container {{
    padding-top: 1rem;
    padding-bottom: 1rem;
}}

/* SPLASH SCREEN */
.splash {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: white;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: fadeOut 2s ease 2s forwards;
    z-index: 9999;
}}

.splash img {{
    width: 380px;
    animation: zoom 2s ease;
}}

@keyframes zoom {{
    from {{transform: scale(0.5); opacity: 0;}}
    to {{transform: scale(1); opacity: 1;}}
}}

@keyframes fadeOut {{
    to {{opacity: 0; visibility: hidden;}}
}}

/* HEADER */
.header {{
    display: flex;
    justify-content: space-between;
    margin-top: -10px;
}}

.logo {{
    height: 110px;
}}

/* TITLES */
.title {{
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: white;
    margin-top: -5px;
}}

.subtitle {{
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    color: #d2f5f0;
    margin-bottom: 15px;
}}

/* LABEL */
label {{
    font-size: 18px !important;
    font-weight: bold;
    color: white !important;
}}

/* SELECT BOX TEXT FIX */
div[data-baseweb="select"] span {{
    color: #004d4d !important;
    font-weight: bold;
}}

/* BUTTON */
.stButton button {{
    background-color: #00bfa5;
    color: white;
    font-size: 16px;
    padding: 8px 20px;
    border-radius: 10px;
}}

/* TOP VENDORS TITLE */
.top-title {{
    font-size: 20px;
    color: white;
    margin-bottom: 10px;
    font-weight: bold;
}}

/* VENDOR BOX (SMALLER) */
.vendor-box {{
    background: white;
    color: #004d40;
    padding: 12px;
    margin: 8px 0;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
}}

</style>
""", unsafe_allow_html=True)

# =====================================
# SPLASH SCREEN
# =====================================
st.markdown(f"""
<div class="splash">
    <img src="data:image/png;base64,{abfrl_logo}">
</div>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================
st.markdown(f"""
<div class="header">
    <img class="logo" src="data:image/png;base64,{abfrl_logo}">
    <img class="logo" src="data:image/png;base64,{pantaloons_logo}">
</div>
""", unsafe_allow_html=True)

# =====================================
# TITLES
# =====================================
st.markdown("<div class='title'>VENDOR RECOMMENDATION SYSTEM</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>YOUNG FASHION</div>", unsafe_allow_html=True)


# =====================================
# LOAD DATA (FINAL FIXED)
# =====================================
df = pd.read_excel("FINAL DATA.xlsx", header=1)

# REMOVE USELESS COLUMN
df = df.loc[:, ~df.columns.str.contains("Unnamed")]

# CLEAN COLUMN NAMES
df.columns = df.columns.str.strip().str.upper()

# DEBUG (optional)
# st.write(df.columns)

# =====================================
# CLEAN DATA
# =====================================
df["FABRIC TYPE"] = df["FABRIC TYPE"].astype(str).str.upper().str.strip()
df["PRODUCT TYPE"] = df["PRODUCT TYPE"].astype(str).str.upper().str.strip()
df["VENDOR NAME"] = df["VENDOR NAME"].astype(str).str.strip()

df = df[["OPTION", "VENDOR NAME", "FABRIC TYPE", "PRODUCT TYPE", "OTIF"]].dropna()

df["OTIF"] = pd.to_numeric(df["OTIF"], errors="coerce")
df = df.dropna()

# =====================================
# GROUP DATA
# =====================================
vendor_stats = df.groupby(
    ["VENDOR NAME", "PRODUCT TYPE", "FABRIC TYPE"]
).agg(
    OPTION_COUNT=("OPTION", "nunique"),
    OTIF_SCORE=("OTIF", "mean")
).reset_index()

# SCORING
vendor_stats["FINAL_SCORE"] = (
    vendor_stats["OPTION_COUNT"] * 0.7 +
    vendor_stats["OTIF_SCORE"] * 100 * 0.3
)

# =====================================
# INPUT + OUTPUT
# =====================================
products = sorted(df["PRODUCT TYPE"].unique())
fabrics = sorted(df["FABRIC TYPE"].unique())

col1, col2 = st.columns([1,2])

with col1:
    product = st.selectbox("PRODUCT TYPE", products)
    fabric = st.selectbox("FABRIC TYPE", fabrics)
    run = st.button("GET VENDORS")

with col2:
    if run:

        data = vendor_stats[
            (vendor_stats["PRODUCT TYPE"] == product) &
            (vendor_stats["FABRIC TYPE"] == fabric)
        ]

        if data.empty:
            st.error("No vendors found")
        else:
            data = data.sort_values("FINAL_SCORE", ascending=False)

            st.markdown("### Top Vendors")

            for i, row in enumerate(data.head(5).itertuples(), start=1):
                badge = "🏆" if i == 1 else "⭐"

                st.markdown(
                    f"<div class='vendor-box'>{badge} {row[1]}</div>",
                    unsafe_allow_html=True
                )

