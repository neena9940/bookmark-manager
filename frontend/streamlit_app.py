import time

import requests
import streamlit as st

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"

# Page config - make it look professional
st.set_page_config(
    page_title="Bookmark Manager Pro",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to make it NOT look like Streamlit
st.markdown(
    """
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Custom styling */
    .stApp {
        background-color: #f5f5f5;
    }

    .bookmark-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    .tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        margin-right: 5px;
        margin-bottom: 5px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None


def get_headers():
    """Get headers with authorization token"""
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def login_page():
    """Login/Register page"""
    st.title("🔖 Bookmark Manager Pro")
    st.markdown("### Welcome back!")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    data={"username": email, "password": password},
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.refresh_token = data["refresh_token"]
                    st.success("Logged in successfully!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    detail = response.json().get("detail", "Unknown error")
                    st.error(f"Login failed: {detail}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")

        if st.button("Register", type="primary", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_URL}/auth/register",
                    json={"email": reg_email, "password": reg_password},
                )

                if response.status_code == 200:
                    st.success("Account created! Please login.")
                else:
                    detail = response.json().get("detail", "Unknown error")
                    st.error(f"Registration failed: {detail}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")


def main_dashboard():
    """Main dashboard after login"""
    # Sidebar
    with st.sidebar:
        st.title("🔖 Bookmark Manager")
        st.markdown(f"**User:** {st.session_state.get('user_email', 'User')}")

        st.markdown("---")

        if st.button(" Logout", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.rerun()

        st.markdown("---")
        st.markdown("### Add New Bookmark")

        with st.form("add_bookmark_form", clear_on_submit=True):
            title = st.text_input("Title")
            url = st.text_input("URL")
            tags = st.text_input(
                "Tags (comma separated)", placeholder="python, backend"
            )
            submitted = st.form_submit_button(
                "Add Bookmark", type="primary", use_container_width=True
            )

            if submitted:
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]

                try:
                    response = requests.post(
                        f"{API_URL}/bookmarks/",
                        headers=get_headers(),
                        json={"title": title, "url": url, "tag_names": tag_list},
                    )

                    if response.status_code == 200:
                        st.success("Bookmark added! AI is generating summary...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Main content
    st.title(" My Bookmarks")

    # Pagination controls
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        page = st.number_input("Page", min_value=1, value=1, step=1)
    with col2:
        size = st.selectbox("Items per page", [10, 20, 50], index=1)
    with col3:
        search = st.text_input("Search")

    # Fetch bookmarks
    try:
        response = requests.get(
            f"{API_URL}/bookmarks/",
            headers=get_headers(),
            params={"page": page, "size": size, "search": search},
        )

        if response.status_code == 200:
            data = response.json()
            bookmarks = data["items"]
            total = data["total"]
            total_pages = data["pages"]

            st.markdown(
                f"**Showing {len(bookmarks)} of {total} bookmarks** "
                f"(Page {page}/{total_pages})"
            )
            st.markdown("---")

            # Display bookmarks
            for bookmark in bookmarks:
                # ✅ Extract long expressions into variables
                tags_html = "".join(
                    [
                        f'<span class="tag">{tag["name"]}</span>'
                        for tag in bookmark.get("tags", [])
                    ]
                )
                created_date = bookmark["created_at"][:10]

                with st.container():
                    st.markdown(
                        f"""
                        <div class="bookmark-card">
                            <h3>{bookmark["title"]}</h3>
                            <p style="color: #666; font-size: 14px">
                                {bookmark["url"]}
                            </p>
                            <p>{bookmark.get("notes", "No summary yet...")}</p>
                            <div>
                                {tags_html}
                            </div>
                            <small style="color: #999">Created: {created_date}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown("---")

            # Navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if page > 1:
                    if st.button("← Previous"):
                        st.rerun()
            with col3:
                if page < total_pages:
                    if st.button("Next →"):
                        st.rerun()

        else:
            st.error(f"Failed to load bookmarks: {response.text}")

    except Exception as e:
        st.error(f"Error loading bookmarks: {str(e)}")


# Main app logic
if st.session_state.access_token:
    main_dashboard()
else:
    login_page()
