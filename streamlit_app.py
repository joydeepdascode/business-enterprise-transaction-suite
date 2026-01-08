import streamlit as st
import pandas as pd
import numpy as np
import math

# Page config
st.set_page_config(
    page_title="<Company-Name> Business - Transaction Suite",
    page_icon="🏢",
    layout="wide"
)

# --- Data & Constants ---
INDUSTRIES = {
    "Manufacturing": {"mult": 4.0, "risk": "Medium", "avgDaysToSell": 180, "premium": 1.1},
    "Tech / SaaS": {"mult": 5.5, "risk": "Low", "avgDaysToSell": 120, "premium": 1.25},
    "Professional Services": {"mult": 3.0, "risk": "Low", "avgDaysToSell": 150, "premium": 1.0},
    "Retail / Main St": {"mult": 2.2, "risk": "Medium-High", "avgDaysToSell": 210, "premium": 0.95},
    "Hospitality / Food": {"mult": 1.8, "risk": "High", "avgDaysToSell": 240, "premium": 0.85},
    "Healthcare": {"mult": 4.5, "risk": "Low", "avgDaysToSell": 165, "premium": 1.15},
    "Construction": {"mult": 3.2, "risk": "Medium", "avgDaysToSell": 195, "premium": 1.05},
    "Distribution": {"mult": 3.8, "risk": "Medium", "avgDaysToSell": 170, "premium": 1.08}
}

OFFICES = ["Boulder (HQ)", "Denver", "Breckenridge", "Golden", "Fort Collins"]
MARKET_TEMPS = ["Cold", "Stable", "Seller's Market", "Hot"]

# Initialize session state
if "current_deal" not in st.session_state:
    st.session_state.current_deal = {
        "entityName": "Boulder Precision Machining",
        "industry": "Manufacturing",
        "revenue": 2_500_000,
        "sde": 650_000,
        "confidentiality": "High"
    }
if "selected_office" not in st.session_state:
    st.session_state.selected_office = "Boulder (HQ)"
if "market_temp" not in st.session_state:
    st.session_state.market_temp = "Stable"
if "buyer_profile" not in st.session_state:
    st.session_state.buyer_profile = {
        "liquidCash": 250_000,
        "creditScore": 720,
        "industryExp": "Relevant"
    }

# --- Helper Functions ---
def calculate_valuation():
    deal = st.session_state.current_deal
    office = st.session_state.selected_office
    market = st.session_state.market_temp

    base_mult = INDUSTRIES[deal["industry"]]["mult"]
    premium = INDUSTRIES[deal["industry"]]["premium"]
    
    location_adj = 1.15 if office == "Boulder (HQ)" else 1.10 if office == "Denver" else 1.0
    market_adj = {"Hot": 1.15, "Seller's Market": 1.08, "Stable": 1.0, "Cold": 0.92}[market]
    
    final_multiple = base_mult * location_adj * market_adj * premium
    return deal["sde"] * final_multiple

def calculate_monthly_payment(principal, rate, years):
    if principal <= 0 or rate <= 0 or years <= 0:
        return 0
    r = (rate / 100) / 12
    n = years * 12
    return (principal * r * (1 + r) ** n) / ((1 + r) ** n - 1)

# --- UI Components ---
st.markdown("<h1 style='text-align: center; color: #1e40af;'>`Company-Name` Business<br><small>Enterprise Transaction Suite</small></h1>", unsafe_allow_html=True)

# Top Controls
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    selected_tab = st.radio(
        "Navigation",
        ["Dashboard", "Valuation", "Buyers", "Marketing", "Due Diligence", "Timeline", "Documents", "Communications"],
        horizontal=True,
        label_visibility="collapsed"
    )
with col2:
    st.session_state.selected_office = st.selectbox("Office", OFFICES, index=OFFICES.index(st.session_state.selected_office))
with col3:
    st.session_state.market_temp = st.selectbox("Market", MARKET_TEMPS, index=MARKET_TEMPS.index(st.session_state.market_temp))

st.divider()

# --- Tab Content ---
if selected_tab == "Dashboard":
    st.subheader("Deal Pipeline Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Listings", "18", "+3 this month")
    col2.metric("Pipeline Value", "$55M", "Total deal value")
    col3.metric("Qualified Buyers", "47", "8 pre-approved")
    col4.metric("Avg. Days to Close", "178", "-12 vs last quarter")

    st.subheader("Analytics")
    pipeline_data = pd.DataFrame({
        "Stage": ["Prospecting", "Initial Consult", "Under Marketing", "LOI Negotiation", "Due Diligence", "Closing"],
        "Count": [12, 8, 5, 3, 2, 1]
    })
    revenue_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Commission": [45000, 62000, 38000, 91000, 73000, 105000]
    })

    c1, c2 = st.columns(2)
    with c1:
        st.bar_chart(pipeline_data.set_index("Stage")["Count"], height=300)
    with c2:
        st.area_chart(revenue_data.set_index("Month")["Commission"], height=300)

elif selected_tab == "Valuation":
    st.subheader("Deal Valuation Calculator")
    deal = st.session_state.current_deal
    c1, c2, c3 = st.columns(3)
    with c1:
        industry = st.selectbox("Industry", list(INDUSTRIES.keys()), index=list(INDUSTRIES.keys()).index(deal["industry"]))
    with c2:
        sde = st.number_input("SDE ($)", min_value=0, value=deal["sde"], step=10000)
    with c3:
        revenue = st.number_input("Revenue ($)", min_value=0, value=deal["revenue"], step=50000)
    
    st.session_state.current_deal.update({"industry": industry, "sde": sde, "revenue": revenue})

    listing_price = calculate_valuation()
    asset_sale_tax = listing_price * 0.20
    net_asset_sale = listing_price - asset_sale_tax
    roi_years = listing_price / sde if sde > 0 else 0

    st.subheader("Financial Analysis")
    col1, col2, col3 = st.columns(3)
    col1.metric("Estimated Listing Price", f"${listing_price:,.0f}", f"{listing_price/sde:.2f}x SDE")
    col2.metric("Net (Asset Sale)", f"${net_asset_sale:,.0f}", f"-${asset_sale_tax:,.0f} tax (20%)")
    col3.metric("Payback Period", f"{roi_years:.1f} yrs", "Based on current SDE")

    st.subheader("Comparable Sales")
    comps = pd.DataFrame({
        "Company": ["Precision Manufacturing Co.", "Mountain Machining LLC", "Apex Industrial Services"],
        "Revenue ($M)": [2.8, 2.2, 3.1],
        "SDE ($K)": [720, 580, 850],
        "Multiple": [4.2, 3.8, 4.5],
        "Days to Sell": [165, 198, 142],
        "Location": ["Denver", "Colorado Springs", "Fort Collins"]
    })
    st.dataframe(comps, use_container_width=True)

elif selected_tab == "Buyers":
    st.subheader("Buyer Qualification")
    buyer = st.session_state.buyer_profile
    c1, c2, c3 = st.columns(3)
    with c1:
        liquid = st.number_input("Liquid Cash ($)", min_value=0, value=buyer["liquidCash"], step=10000)
    with c2:
        credit = st.number_input("Credit Score", min_value=300, max_value=850, value=buyer["creditScore"])
    with c3:
        exp = st.selectbox("Industry Experience", ["Novice", "Relevant", "Expert"], index=["Novice", "Relevant", "Expert"].index(buyer["industryExp"]))
    st.session_state.buyer_profile.update({"liquidCash": liquid, "creditScore": credit, "industryExp": exp})

    listing_price = calculate_valuation()
    sba_min = listing_price * 0.10
    conv_min = listing_price * 0.25
    qualifies_sba = liquid >= sba_min and credit >= 680
    qualifies_conv = liquid >= conv_min

    st.subheader("Financing Options")
    options = []
    for name, down, rate, term, qualified in [
        ("SBA 7(a) Loan", sba_min, 11.5, 10, qualifies_sba),
        ("Conventional Bank", conv_min, 9.25, 7, qualifies_conv),
        ("Seller Financing", listing_price * 0.15, 8.0, 5, True)
    ]:
        loan = listing_price - down
        monthly = calculate_monthly_payment(loan, rate, term)
        dscr = (st.session_state.current_deal["sde"] / (monthly * 12)) if monthly > 0 else 0
        status = "✅ Qualified" if qualified else "❌ Not Qualified"
        color = "green" if qualified else "red"
        options.append({
            "Option": name,
            "Down Payment": f"${down:,.0f}",
            "Loan Amount": f"${loan:,.0f}",
            "Rate (%)": rate,
            "Monthly": f"${monthly:,.0f}",
            "DSCR": f"{dscr:.2f}x",
            "Status": status
        })
    df = pd.DataFrame(options)
    st.dataframe(df.style.apply(lambda x: [
        "background-color: #d1fad1" if "✅" in x.Status else "background-color: #fad1d1" for _ in x
    ], axis=1), use_container_width=True)

elif selected_tab == "Marketing":
    st.subheader("Confidentiality Settings")
    conf = st.selectbox(
        "Confidentiality Level",
        ["Low", "Moderate", "High", "Extreme"],
        index=["Low", "Moderate", "High", "Extreme"].index(st.session_state.current_deal["confidentiality"])
    )
    st.session_state.current_deal["confidentiality"] = conf

    if conf == "Extreme":
        st.warning("⚠️ **High Risk**: Blind profiles only. No company name, location details, or specific industry identifiers until NDA signed.")
    elif conf == "High":
        st.info("ℹ️ **Moderate Risk**: Limited disclosure. General industry and region only. Detailed financials after NDA.")

    st.subheader("Marketing Teaser (AI-Generated)")
    revenue_m = st.session_state.current_deal["revenue"] / 1_000_000
    prefix = "Confidential" if conf == "Extreme" else "Established"
    teaser = f"{prefix} {st.session_state.current_deal['industry']} business opportunity in thriving Colorado market. Strong revenue of ${revenue_m:.1f}M+ with excellent management team in place. Ideal for strategic buyer or add-on acquisition. Serious inquiries only - NDA required."
    st.text_area("Teaser", teaser, height=100, disabled=True)

    st.subheader("Marketing Channel Recommendations")
    channels = pd.DataFrame({
        "Channel": ["BizBuySell Premium", "FRB Internal Database", "LinkedIn Targeted Ads", "Industry Trade Publications", "Direct Competitor Outreach", "Business Broker Network"],
        "Cost ($)": [799, 0, 1200, 2500, 500, 0],
        "Reach": ["High", "Medium", "High", "Medium", "Low", "Medium"],
        "Lead Quality": ["Medium", "High", "High", "Very High", "Very High", "High"]
    })
    st.dataframe(channels, use_container_width=True)

elif selected_tab == "Due Diligence":
    st.subheader("Due Diligence Tracker")
    checklist = {
        "Financial": [
            {"item": "3 Years Tax Returns", "status": "complete"},
            {"item": "P&L Statements (Monthly)", "status": "pending"},
            {"item": "Balance Sheet", "status": "pending"},
            {"item": "A/R Aging Report", "status": "incomplete"},
            {"item": "A/P Aging Report", "status": "incomplete"},
            {"item": "Bank Statements (12 months)", "status": "pending"}
        ],
        "Legal": [
            {"item": "Articles of Incorporation", "status": "complete"},
            {"item": "Operating Agreement / Bylaws", "status": "pending"},
            {"item": "Material Contracts Review", "status": "incomplete"},
            {"item": "Lease Agreements", "status": "pending"},
            {"item": "Intellectual Property Documentation", "status": "incomplete"},
            {"item": "Litigation History", "status": "complete"}
        ],
        "Operations": [
            {"item": "Customer Concentration Analysis", "status": "complete"},
            {"item": "Employee Roster & Compensation", "status": "pending"},
            {"item": "Equipment List & Condition", "status": "incomplete"},
            {"item": "Key Vendor Relationships", "status": "pending"},
            {"item": "Standard Operating Procedures", "status": "incomplete"}
        ]
    }

    def status_color(s):
        return {"complete": "green", "pending": "orange", "incomplete": "red"}.get(s, "gray")

    for category, items in checklist.items():
        done = sum(1 for i in items if i["status"] == "complete")
        pct = int((done / len(items)) * 100)
        st.write(f"**{category} Documents**")
        st.progress(pct / 100)
        for item in items:
            icon = "✅" if item["status"] == "complete" else "⏳" if item["status"] == "pending" else "❌"
            st.markdown(f"{icon} {item['item']}")

elif selected_tab == "Timeline":
    st.subheader("Transaction Progress")
    milestones = [
        {"phase": "Engagement & Valuation", "days": 14, "status": "complete", "date": "2024-01-05"},
        {"phase": "Marketing Preparation", "days": 21, "status": "complete", "date": "2024-01-19"},
        {"phase": "Active Marketing", "days": 60, "status": "in-progress", "date": "2024-03-20"},
        {"phase": "LOI Negotiation", "days": 14, "status": "upcoming", "date": "2024-04-03"},
        {"phase": "Due Diligence", "days": 45, "status": "upcoming", "date": "2024-05-18"},
        {"phase": "Legal & Financing", "days": 30, "status": "upcoming", "date": "2024-06-17"},
        {"phase": "Closing", "days": 7, "status": "upcoming", "date": "2024-06-24"}
    ]
    total = sum(m["days"] for m in milestones)
    completed = sum(m["days"] for m in milestones if m["status"] == "complete")
    progress = completed / total if total > 0 else 0
    st.progress(progress)
    st.caption(f"Estimated closing: {milestones[-1]['date']}")

    st.subheader("Deal Milestones")
    for i, m in enumerate(milestones):
        icon = "✅" if m["status"] == "complete" else "🔵" if m["status"] == "in-progress" else "🔲"
        status_color = "green" if m["status"] == "complete" else "blue" if m["status"] == "in-progress" else "gray"
        st.markdown(f"**{icon} {m['phase']}** ({m['days']} days) — *Target: {m['date']}*")
        if i < len(milestones) - 1:
            st.markdown("---")

elif selected_tab == "Documents":
    st.subheader("Document Vault")
    docs = pd.DataFrame({
        "Name": [
            "CIM - Confidential Info Memo.pdf",
            "Tax Returns 2021-2023.zip",
            "Lease Agreement - Main Facility.pdf",
            "Equipment Appraisal Report.pdf",
            "Customer List (Anonymized).xlsx"
        ],
        "Category": ["Marketing", "Financial", "Legal", "Operations", "Operations"],
        "Size": ["2.4 MB", "8.1 MB", "1.2 MB", "3.7 MB", "245 KB"],
        "Uploaded": ["2024-01-05", "2024-01-03", "2024-01-02", "2023-12-28", "2024-01-04"],
        "Status": ["Active", "Verified", "Active", "Active", "Active"]
    })
    st.dataframe(docs, use_container_width=True)
    st.button("📤 Upload Document")

elif selected_tab == "Communications":
    st.subheader("Communication Log")
    comms = pd.DataFrame({
        "Date": [
            "2024-01-08 10:30 AM",
            "2024-01-07 2:15 PM",
            "2024-01-06 9:00 AM",
            "2024-01-05 4:45 PM"
        ],
        "Type": ["Email", "Phone", "Meeting", "Email"],
        "Contact": [
            "John Smith (Seller)",
            "Sarah Johnson (Buyer)",
            "John Smith (Seller)",
            "Mike Davis (Buyer)"
        ],
        "Subject": [
            "Updated financials received",
            "Initial interest call - 25 minutes",
            "Valuation review meeting",
            "NDA signed and returned"
        ],
        "Priority": ["Normal", "High", "High", "Normal"]
    })
    st.dataframe(comms.style.apply(lambda x: [
        "background-color: #ffebee" if x.Priority == "High" else "" for _ in x
    ], axis=1), use_container_width=True)
    st.button("✉️ Log Communication")

# Footer
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("© 2026 <Company-Name> Business Advisors")
with col2:
    st.button("💾 Save to CRM")
    st.button("📥 Export Report")
