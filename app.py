import streamlit as st
import pandas as pd
import pyodbc

# 1. ตั้งค่าหน้าเพจให้กว้างสุด
st.set_page_config(page_title="Crypto Gem Dashboard", page_icon="🚀", layout="wide")

st.title("🚀 Crypto Trading Dashboard")
st.markdown("ระบบวิเคราะห์สัญญาณเทรดและประเมินความเสี่ยงอัตโนมัติ")

# 2. ฟังก์ชันดึงข้อมูลจาก Azure SQL
# ใช้ @st.cache_data เพื่อให้ระบบจำข้อมูลไว้ชั่วคราว เว็บจะได้ไม่ช้า
@st.cache_data(ttl=300) # อัปเดตข้อมูลใหม่ทุกๆ 5 นาที
def load_data():
    # เปลี่ยนข้อมูลตรงนี้เป็นของ Azure SQL คุณครับ
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=databrick-dashborad.database.windows.net;"
        "DATABASE=dashboard-crypto-2;"
        "UID=wongsatorn;"
        "PWD=Ton_33429;"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        query = "SELECT Pair, MarketCap, TA_Signal, Total_Gem_Score, Risk_Level, Suggested_Entry FROM crypto.dashboard"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Database: {e}")

df = load_data()

# 3. สร้าง Filter ด้านซ้ายมือ (Sidebar)
st.sidebar.header("🔍 กรองข้อมูล (Filters)")

# Filter: ระดับความเสี่ยง
selected_risk = st.sidebar.multiselect(
    "เลือกระดับความเสี่ยง (Risk Level):",
    options=df['Risk_Level'].unique(),
    default=df['Risk_Level'].unique()
)

# Filter: สัญญาณเทรด
selected_signal = st.sidebar.multiselect(
    "เลือกสัญญาณ (TA Signal):",
    options=df['TA_Signal'].unique(),
    default=df['TA_Signal'].unique()
)

# นำ Filter มาตัด Dataframe
df_filtered = df[(df['Risk_Level'].isin(selected_risk)) & (df['TA_Signal'].isin(selected_signal))]

# 4. แสดงผล KPI (ตัวเลขสรุปด้านบน)
st.subheader("📊 สรุปภาพรวม (Overview)")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("จำนวนเหรียญที่พบ", f"{len(df_filtered)} Pairs")
with col2:
    st.metric("เหรียญที่มีสัญญาณ Buy", f"{len(df_filtered[df_filtered['TA_Signal'] == 'Buy'])} Pairs")
# with col3:
#     avg_score = df_filtered['Total_Gem_Score'].mean()
#     st.metric("คะแนน Gem Score เฉลี่ย", f"{avg_score:.2f}" if not pd.isna(avg_score) else "0.00")

st.divider()

# 5. แสดงผลตารางข้อมูลแบบ Interactive (Sort ได้, ค้นหาได้)
st.subheader("📋 ตารางข้อมูลเหรียญ (Data Table)")
st.dataframe(
    df_filtered,
    use_container_width=True,
    column_config={
        "Pair": st.column_config.TextColumn("เหรียญ (Pair)"),
        "MarketCap": st.column_config.NumberColumn("Market Cap ($)", format="%d"),
        "TA_Signal": st.column_config.TextColumn("สัญญาณ (Signal)"),
        "Total_Gem_Score": st.column_config.ProgressColumn("Gem Score", format="%f", min_value=0, max_value=100),
        "Risk_Level": st.column_config.TextColumn("ความเสี่ยง"),
        "Suggested_Entry": st.column_config.NumberColumn("จุดเข้าที่แนะนำ ($)", format="%.4f")
    },
    hide_index=True
)