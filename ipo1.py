import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# ---------- Config ----------

DATA_IPO_FILE = "ipos.csv"
DATA_RATINGS_FILE = "ipo_ratings.csv"

st.set_page_config(
    page_title="IPO Review & Scorecard",
    page_icon="📊",
    layout="wide",
)


# ---------- Data helpers ----------

def init_ipo_data() -> pd.DataFrame:
    """Create a sample IPO dataset if file does not exist."""
    if os.path.exists(DATA_IPO_FILE):
        df = pd.read_csv(DATA_IPO_FILE, parse_dates=["open_date", "close_date", "listing_date"])
        return df

    data = [
        {
            "ipo_id": 1,
            "company_name": "Alpha Tech Solutions Ltd",
            "symbol": "ALPHATECH",
            "sector": "Technology",
            "issue_size_crores": 1200,
            "price_band_low": 110,
            "price_band_high": 120,
            "lot_size": 125,
            "open_date": "2025-01-10",
            "close_date": "2025-01-12",
            "listing_date": "2025-01-18",
            "status": "Upcoming",
            "face_value": 10,
            "issue_type": "Book Built Issue IPO",
            "registrar": "Big Registrar Services",
            "description": "Mid-size IT services and product company with focus on cloud and analytics.",
            "industry_pe": 28.5,
            "expected_pe": 32.0,
            "post_issue_market_cap_crores": 4500,
        },
        {
            "ipo_id": 2,
            "company_name": "GreenMart Retail Ltd",
            "symbol": "GREENMART",
            "sector": "Retail",
            "issue_size_crores": 800,
            "price_band_low": 80,
            "price_band_high": 86,
            "lot_size": 175,
            "open_date": "2024-10-03",
            "close_date": "2024-10-05",
            "listing_date": "2024-10-11",
            "status": "Listed",
            "face_value": 10,
            "issue_type": "Book Built Issue IPO",
            "registrar": "Secure Registrar Pvt Ltd",
            "description": "Supermarket chain focused on Tier-2 and Tier-3 cities.",
            "industry_pe": 35.0,
            "expected_pe": 42.0,
            "post_issue_market_cap_crores": 3200,
        },
        {
            "ipo_id": 3,
            "company_name": "SolidBuild Infra Ltd",
            "symbol": "SOLIDINFRA",
            "sector": "Infrastructure",
            "issue_size_crores": 1500,
            "price_band_low": 220,
            "price_band_high": 230,
            "lot_size": 65,
            "open_date": "2024-08-20",
            "close_date": "2024-08-22",
            "listing_date": "2024-08-28",
            "status": "Listed",
            "face_value": 10,
            "issue_type": "Book Built Issue IPO",
            "registrar": "Trust Registrar Ltd",
            "description": "EPC player in roads and bridges with a strong order book.",
            "industry_pe": 20.0,
            "expected_pe": 18.0,
            "post_issue_market_cap_crores": 6000,
        },
    ]
    df = pd.DataFrame(data)
    df["open_date"] = pd.to_datetime(df["open_date"])
    df["close_date"] = pd.to_datetime(df["close_date"])
    df["listing_date"] = pd.to_datetime(df["listing_date"])

    df.to_csv(DATA_IPO_FILE, index=False)
    return df


def load_ratings() -> pd.DataFrame:
    if not os.path.exists(DATA_RATINGS_FILE):
        cols = ["ipo_id", "rating", "risk_level", "sentiment", "comment", "timestamp"]
        empty = pd.DataFrame(columns=cols)
        empty.to_csv(DATA_RATINGS_FILE, index=False)
        return empty
    df = pd.read_csv(DATA_RATINGS_FILE)
    return df


def save_rating(ipo_id: int, rating: int, risk_level: int, sentiment: str, comment: str):
    df = load_ratings()
    new_row = {
        "ipo_id": ipo_id,
        "rating": rating,
        "risk_level": risk_level,
        "sentiment": sentiment,
        "comment": comment,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_RATINGS_FILE, index=False)


# ---------- GMP (Grey Market Premium) helpers ----------

def load_gmp_data() -> pd.DataFrame:
    """
    Stub GMP data. In a real app you would:
    - pull from a Google Sheet / database / API
    For now we keep static demo data.
    """
    data = [
        {"ipo_id": 1, "date": "2024-12-20", "gmp_rs": 45},
        {"ipo_id": 1, "date": "2024-12-21", "gmp_rs": 60},
        {"ipo_id": 1, "date": "2024-12-22", "gmp_rs": 55},
        {"ipo_id": 2, "date": "2024-10-01", "gmp_rs": 25},
        {"ipo_id": 2, "date": "2024-10-02", "gmp_rs": 30},
        {"ipo_id": 3, "date": "2024-08-18", "gmp_rs": -5},
        {"ipo_id": 3, "date": "2024-08-19", "gmp_rs": 0},
    ]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_latest_gmp(gmp_df: pd.DataFrame, ipo_id: int):
    subset = gmp_df[gmp_df["ipo_id"] == ipo_id].sort_values("date")
    if subset.empty:
        return None
    latest = subset.iloc[-1]
    return latest["gmp_rs"], latest["date"]


# ---------- UI helpers ----------

def render_header():
    st.markdown(
        """
        <h1 style="margin-bottom:0">📊 IPO Review & Scorecard</h1>
        <p style="color:gray;margin-top:4px;">
        Track IPO details, grey market premium (GMP), valuation, and real crowd sentiment in one simple dashboard.
        </p>
        <hr/>
        """,
        unsafe_allow_html=True,
    )


def render_ipo_list(df_ipos: pd.DataFrame, gmp_df: pd.DataFrame):
    st.subheader("IPO Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            options=["All", "Upcoming", "Ongoing", "Listed"],
            index=0,
        )
    with col2:
        sector_filter = st.selectbox(
            "Filter by sector",
            options=["All"] + sorted(df_ipos["sector"].dropna().unique().tolist()),
        )
    with col3:
        search_text = st.text_input("Search by company / symbol")

    df = df_ipos.copy()

    # Derive Ongoing if today between open and close
    today = pd.Timestamp.today().normalize()
    df["derived_status"] = df["status"]
    mask_ongoing = (df["open_date"] <= today) & (df["close_date"] >= today)
    df.loc[mask_ongoing, "derived_status"] = "Ongoing"

    if status_filter != "All":
        df = df[df["derived_status"] == status_filter]

    if sector_filter != "All":
        df = df[df["sector"] == sector_filter]

    if search_text:
        s = search_text.lower()
        df = df[
            df["company_name"].str.lower().str.contains(s)
            | df["symbol"].str.lower().str.contains(s)
        ]

    # Attach latest GMP
    latest_gmps = []
    for _, row in df.iterrows():
        latest = get_latest_gmp(gmp_df, row["ipo_id"])
        latest_gmps.append(latest[0] if latest else None)
    df["latest_gmp"] = latest_gmps

    display_cols = [
        "company_name",
        "symbol",
        "sector",
        "issue_size_crores",
        "price_band_low",
        "price_band_high",
        "open_date",
        "close_date",
        "derived_status",
        "latest_gmp",
    ]
    df_view = df[display_cols].rename(
        columns={
            "company_name": "Company",
            "symbol": "Symbol",
            "sector": "Sector",
            "issue_size_crores": "Issue Size (₹ Cr)",
            "price_band_low": "Price Low (₹)",
            "price_band_high": "Price High (₹)",
            "open_date": "Opens",
            "close_date": "Closes",
            "derived_status": "Status",
            "latest_gmp": "Latest GMP (₹)",
        }
    )

    st.dataframe(
        df_view,
        use_container_width=True,
        hide_index=True,
    )

    st.caption("Tip: Click on a company from the dropdown below to see full details and crowd sentiment.")

    selected_company = st.selectbox(
        "View details for",
        options=["-- Select an IPO --"] + df_ipos["company_name"].tolist(),
        index=0,
    )

    if selected_company != "-- Select an IPO --":
        ipo_row = df_ipos[df_ipos["company_name"] == selected_company].iloc[0]
        render_ipo_detail(ipo_row, gmp_df)


def render_ipo_detail(ipo_row: pd.Series, gmp_df: pd.DataFrame):
    st.markdown("---")
    st.subheader(f"📌 {ipo_row['company_name']} ({ipo_row['symbol']})")

    col_main, col_side = st.columns([2, 1])

    latest = get_latest_gmp(gmp_df, ipo_row["ipo_id"])
    latest_gmp, gmp_date = (latest if latest else (None, None))

    with col_main:
        st.markdown("**Basic Details**")
        info_cols = st.columns(3)
        info_cols[0].metric("Issue Size (₹ Cr)", f"{ipo_row['issue_size_crores']:,}")
        info_cols[1].metric(
            "Price Band (₹)", f"{ipo_row['price_band_low']} - {ipo_row['price_band_high']}"
        )
        info_cols[2].metric("Lot Size", int(ipo_row["lot_size"]))

        info_cols2 = st.columns(3)
        info_cols2[0].metric("Opens", ipo_row["open_date"].strftime("%d %b %Y"))
        info_cols2[1].metric("Closes", ipo_row["close_date"].strftime("%d %b %Y"))
        info_cols2[2].metric("Listing Date", ipo_row["listing_date"].strftime("%d %b %Y"))

        st.markdown("**Business Overview**")
        st.write(ipo_row["description"])

        st.markdown("**Valuation Snapshot**")
        val_cols = st.columns(3)
        val_cols[0].metric("Industry P/E", f"{ipo_row['industry_pe']:.1f}x")
        val_cols[1].metric("IPO P/E (expected)", f"{ipo_row['expected_pe']:.1f}x")
        prem_discount = ipo_row["expected_pe"] - ipo_row["industry_pe"]
        label = "Premium vs Industry" if prem_discount >= 0 else "Discount vs Industry"
        val_cols[2].metric(label, f"{prem_discount:+.1f}x")

        st.caption(
            "Note: Valuation numbers are for educational use only and not investment advice."
        )

    with col_side:
        st.markdown("**Grey Market Premium (GMP)**")
        if latest_gmp is not None:
            st.metric(
                "Latest GMP (₹)",
                f"{latest_gmp:+.0f}",
                help=f"As of {gmp_date.strftime('%d %b %Y')}",
            )
        else:
            st.info("No GMP data available for this IPO yet.")

        # Plot GMP trend
        ipo_gmp = gmp_df[gmp_df["ipo_id"] == ipo_row["ipo_id"]].sort_values("date")
        if not ipo_gmp.empty:
            fig = px.line(
                ipo_gmp,
                x="date",
                y="gmp_rs",
                markers=True,
                labels={"date": "Date", "gmp_rs": "GMP (₹)"},
                title="GMP Trend",
            )
            fig.update_layout(height=260, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("**IPO Details**")
        st.write(
            f"- Sector: **{ipo_row['sector']}**  \n"
            f"- Issue Type: **{ipo_row['issue_type']}**  \n"
            f"- Face Value: **₹{ipo_row['face_value']}** per share  \n"
            f"- Post Issue Market Cap: **₹{ipo_row['post_issue_market_cap_crores']:,} Cr**  \n"
            f"- Registrar: **{ipo_row['registrar']}**"
        )

    # Crowd sentiment & ratings section
    st.markdown("### 🧠 Crowd Rating & Sentiment")
    render_crowd_sentiment(ipo_row["ipo_id"])


def render_crowd_sentiment(ipo_id: int):
    ratings_df = load_ratings()
    ipo_ratings = ratings_df[ratings_df["ipo_id"] == ipo_id]

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("#### Submit your view")
        rating = st.slider("Overall rating (1 = Poor, 5 = Excellent)", 1, 5, 4)
        risk_level = st.slider("Risk level (1 = Very Low, 5 = Very High)", 1, 5, 3)
        sentiment = st.selectbox("Your sentiment", ["Bullish", "Neutral", "Bearish"])
        comment = st.text_area("Short note (optional)")

        if st.button("Submit rating", use_container_width=True):
            save_rating(ipo_id, rating, risk_level, sentiment, comment)
            st.success("Thanks! Your rating has been recorded. Refresh to see updated sentiment.")

    with col_right:
        st.markdown("#### Crowd snapshot")
        if ipo_ratings.empty:
            st.info("No ratings yet. Be the first to share your view!")
        else:
            avg_rating = ipo_ratings["rating"].mean()
            avg_risk = ipo_ratings["risk_level"].mean()
            total_votes = len(ipo_ratings)

            bullish_pct = (
                (ipo_ratings["sentiment"] == "Bullish").sum() / total_votes * 100
            )
            neutral_pct = (
                (ipo_ratings["sentiment"] == "Neutral").sum() / total_votes * 100
            )
            bearish_pct = 100 - bullish_pct - neutral_pct

            st.metric("Average Rating", f"{avg_rating:.1f} / 5")
            st.metric("Average Risk", f"{avg_risk:.1f} / 5")
            st.caption(f"Based on {total_votes} community votes.")

            st.progress(int(bullish_pct), text=f"🐂 Bullish: {bullish_pct:.0f}%")
            st.progress(int(neutral_pct), text=f"😐 Neutral: {neutral_pct:.0f}%")
            st.progress(int(bearish_pct), text=f"🐻 Bearish: {bearish_pct:.0f}%")

    with st.expander("Recent comments"):
        if ipo_ratings.empty:
            st.write("No comments yet.")
        else:
            sorted_comments = ipo_ratings.sort_values("timestamp", ascending=False).head(10)
            for _, row in sorted_comments.iterrows():
                st.markdown(
                    f"**{row['sentiment']} • {row['rating']}/5 • Risk {row['risk_level']}/5**  \n"
                    f"<span style='color:gray;font-size:12px'>{row['timestamp']}</span>",
                    unsafe_allow_html=True,
                )
                if isinstance(row["comment"], str) and row["comment"].strip():
                    st.write(row["comment"])
                st.markdown("---")


def render_admin_page(df_ipos: pd.DataFrame):
    st.subheader("Admin: Manage IPO List (Local Only)")
    st.caption(
        "This is a simple local editor that writes to `ipos.csv` in the app folder. "
        "On Streamlit Cloud, data will reset when you redeploy."
    )

    st.dataframe(df_ipos, use_container_width=True)

    with st.expander("Add new IPO"):
        with st.form("add_ipo_form"):
            company_name = st.text_input("Company name")
            symbol = st.text_input("Symbol (ticker)")
            sector = st.text_input("Sector")
            issue_size_crores = st.number_input("Issue size (₹ Cr)", min_value=0.0, step=10.0)
            price_band_low = st.number_input("Price band low (₹)", min_value=0.0, step=1.0)
            price_band_high = st.number_input("Price band high (₹)", min_value=0.0, step=1.0)
            lot_size = st.number_input("Lot size", min_value=1, step=1)
            open_date = st.date_input("Open date")
            close_date = st.date_input("Close date")
            listing_date = st.date_input("Listing date")
            face_value = st.number_input("Face value (₹)", min_value=1.0, step=1.0, value=10.0)
            issue_type = st.text_input("Issue type", value="Book Built Issue IPO")
            registrar = st.text_input("Registrar")
            description = st.text_area("Short description")
            industry_pe = st.number_input("Industry P/E", min_value=0.0, step=0.1)
            expected_pe = st.number_input("IPO P/E (expected)", min_value=0.0, step=0.1)
            post_issue_market_cap_crores = st.number_input(
                "Post issue market cap (₹ Cr)", min_value=0.0, step=10.0
            )

            submitted = st.form_submit_button("Add IPO")
            if submitted:
                if not company_name or not symbol:
                    st.error("Company name and symbol are required.")
                else:
                    new_id = int(df_ipos["ipo_id"].max()) + 1 if not df_ipos.empty else 1
                    new_row = {
                        "ipo_id": new_id,
                        "company_name": company_name,
                        "symbol": symbol,
                        "sector": sector,
                        "issue_size_crores": issue_size_crores,
                        "price_band_low": price_band_low,
                        "price_band_high": price_band_high,
                        "lot_size": lot_size,
                        "open_date": pd.to_datetime(open_date),
                        "close_date": pd.to_datetime(close_date),
                        "listing_date": pd.to_datetime(listing_date),
                        "status": "Upcoming",
                        "face_value": face_value,
                        "issue_type": issue_type,
                        "registrar": registrar,
                        "description": description,
                        "industry_pe": industry_pe,
                        "expected_pe": expected_pe,
                        "post_issue_market_cap_crores": post_issue_market_cap_crores,
                    }
                    df_new = pd.concat([df_ipos, pd.DataFrame([new_row])], ignore_index=True)
                    df_new.to_csv(DATA_IPO_FILE, index=False)
                    st.success("IPO added. Please rerun the app to see it in the dashboard.")


def main():
    df_ipos = init_ipo_data()
    gmp_df = load_gmp_data()

    render_header()

    page = st.sidebar.radio(
        "Navigation",
        options=["IPO Dashboard", "Admin (local)"],
        index=0,
    )

    if page == "IPO Dashboard":
        render_ipo_list(df_ipos, gmp_df)
    else:
        render_admin_page(df_ipos)


if __name__ == "__main__":
    main()
