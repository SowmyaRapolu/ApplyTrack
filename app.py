
import streamlit as st
import pandas as pd
import plotly.express as px
import database

# Page configuration
# Custom CSS Styling
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #F0F4FA;
    }

    [data-testid="stMetric"] {
        background-color: #F5F7FC;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }

    h1, h2, h3 {
        color: #243B64;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
database.create_table()

# Sidebar navigation
st.sidebar.title("💼 ApplyTrack")
st.sidebar.caption("Your Personal Job Tracker")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Application",
        "My Applications",
        "Analytics"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Built with Python, Streamlit and SQLite")

# Fetch application records
jobs = database.get_applications()

# Convert records into a DataFrame
df = pd.DataFrame(
    jobs,
    columns=[
        "ID",
        "Company",
        "Role",
        "Status",
        "Job Link",
        "Applied Date"
    ]
)

# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.title("📊 Dashboard")
    st.write("Welcome to your job application overview.")

    total = len(jobs)
    interviews = sum(job[3] == "Interview" for job in jobs)
    offers = sum(job[3] == "Offer" for job in jobs)
    rejections = sum(job[3] == "Rejected" for job in jobs)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Applications", total)
    col2.metric("Interviews", interviews)
    col3.metric("Offers", offers)
    col4.metric("Rejections", rejections)

    st.divider()
    st.subheader("Recent Applications")

    if jobs:
        st.dataframe(
            df.sort_values("ID", ascending=False).head(5),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No applications yet. Start by adding your first application!")

# ---------------- ADD APPLICATION ----------------

elif page == "Add Application":

    st.title("➕ Add New Application")
    st.write("Record a new job opportunity.")

    with st.form("application_form"):

        company = st.text_input("Company Name")
        role = st.text_input("Job Role")

        status = st.selectbox(
            "Application Status",
            ["Applied", "Assessment", "Interview", "Offer", "Rejected"]
        )

        job_link = st.text_input("Job Link")

        submitted = st.form_submit_button("Add Application")

        if submitted:

            if company.strip() and role.strip():

                database.add_application(
                    company.strip(),
                    role.strip(),
                    status,
                    job_link.strip()
                )

                st.success("Application added successfully!")
                st.rerun()

            else:
                st.warning("Please enter company name and job role.")

# ---------------- MY APPLICATIONS ----------------

elif page == "My Applications":

    st.title("📋 My Applications")

    if jobs:

        search = st.text_input("🔍 Search by company name")

        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Applied", "Assessment", "Interview", "Offer", "Rejected"]
        )

        filtered_df = df[
            df["Company"].str.contains(search, case=False, na=False)
        ]

        if status_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Status"] == status_filter
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Edit application
        st.subheader("✏️ Edit Application")

        selected_id = st.selectbox(
            "Select Application ID",
            [job[0] for job in jobs]
        )

        selected_job = next(
            job for job in jobs if job[0] == selected_id
        )

        with st.form("edit_form"):

            edit_company = st.text_input(
                "Company",
                value=selected_job[1]
            )

            edit_role = st.text_input(
                "Job Role",
                value=selected_job[2]
            )

            statuses = [
                "Applied", "Assessment", "Interview", "Offer", "Rejected"
            ]

            edit_status = st.selectbox(
                "Status",
                statuses,
                index=statuses.index(selected_job[3])
                if selected_job[3] in statuses else 0
            )

            edit_link = st.text_input(
                "Job Link",
                value=selected_job[4] or ""
            )

            update_button = st.form_submit_button("Update Application")

            if update_button:

                if edit_company.strip() and edit_role.strip():

                    database.update_application(
                        selected_id,
                        edit_company.strip(),
                        edit_role.strip(),
                        edit_status,
                        edit_link.strip()
                    )

                    st.success("Application updated!")
                    st.rerun()

                else:
                    st.warning("Company and role are required.")

        st.divider()

        # Delete application
        st.subheader("🗑️ Delete Application")

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this application."
        )

        if st.button("Delete Selected Application"):

            if confirm_delete:
                database.delete_application(selected_id)
                st.success("Application deleted!")
                st.rerun()

            else:
                st.warning("Please confirm before deleting.")

    else:
        st.info("No applications available. Add your first application!")

# ---------------- ANALYTICS ----------------

elif page == "Analytics":

    st.title("📈 Application Analytics")
    st.write("Understand your job search progress.")

    if jobs:

        # Applications by status
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig = px.bar(
            status_counts,
            x="Status",
            y="Count",
            title="Applications by Status",
            text="Count"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Applications by company
        company_counts = df["Company"].value_counts().reset_index()
        company_counts.columns = ["Company", "Count"]

        fig2 = px.pie(
            company_counts,
            names="Company",
            values="Count",
            title="Applications by Company"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # Monthly application trend
        df["Applied Date"] = pd.to_datetime(
            df["Applied Date"],
            errors="coerce"
        )

        monthly_data = df.dropna(subset=["Applied Date"]).copy()

        if not monthly_data.empty:

            monthly_data["Month"] = (
                monthly_data["Applied Date"].dt.to_period("M").astype(str)
            )

            monthly_counts = (
                monthly_data.groupby("Month")
                .size()
                .reset_index(name="Applications")
            )

            fig3 = px.line(
                monthly_counts,
                x="Month",
                y="Applications",
                markers=True,
                title="Monthly Application Trend"
            )

            st.plotly_chart(fig3, use_container_width=True)

        else:
            st.info("Monthly trends will appear when application dates are available.")

    else:
        st.info("Add applications to see your analytics.")
