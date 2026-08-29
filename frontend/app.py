import requests
import streamlit as st

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="AI Bookmark Manager", layout="wide")


# --- Helper Functions ---
def login(email, password):
    response = requests.post(
        f"{API_URL}/auth/login", data={"username": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def get_headers(token):
    return {"Authorization": f"Bearer {token}"}


def get_tags(token):
    try:
        response = requests.get(f"{API_URL}/tags/", headers=get_headers(token))
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching tags: {e}")
    return []


def create_bookmark(token, title, url, tag_id=None):
    payload = {
        "title": title,
        "url": url,
        "notes": None,  # Let the AI handle it!
        "tag_id": tag_id,
    }
    try:
        response = requests.post(
            f"{API_URL}/bookmarks/", headers=get_headers(token), json=payload
        )
        return (
            response.status_code == 200,
            response.json() if response.status_code == 200 else None,
        )
    except Exception as e:
        st.error(f"Error creating bookmark: {e}")
        return False, None


def get_bookmarks(token):
    try:
        response = requests.get(f"{API_URL}/bookmarks/", headers=get_headers(token))
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching bookmarks: {e}")
    return []


# --- App Logic ---
def main():
    st.title("🤖 AI-Powered Bookmark Manager")

    # Initialize session state
    if "token" not in st.session_state:
        st.session_state.token = None

    # Sidebar for Login/Logout
    with st.sidebar:
        st.header("User Session")
        if st.session_state.token:
            st.success("Logged in!")
            if st.button("Logout"):
                st.session_state.token = None
                st.rerun()
        else:
            st.warning("Please log in to continue.")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                token = login(email, password)
                if token:
                    st.session_state.token = token
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    # Main Content (Only if logged in)
    if st.session_state.token:
        token = st.session_state.token

        # Create Bookmark Section
        st.subheader("Add New Bookmark")
        with st.form("add_bookmark_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Title")
            with col2:
                url = st.text_input("URL")

            # Fetch tags for dropdown
            tags = get_tags(token)

            if tags:
                tag_options = {tag["name"]: tag["id"] for tag in tags}
                selected_tag = st.selectbox(
                    "Select Tag (Optional)", options=["None"] + list(tag_options.keys())
                )
                tag_id = (
                    tag_options.get(selected_tag) if selected_tag != "None" else None
                )
            else:
                st.info(
                    "No tags found. Create bookmarks with tags via the API."
                )
                tag_id = None

            submitted = st.form_submit_button("Save & Generate AI Summary")

            if submitted:
                if not title or not url:
                    st.error("Please fill in title and URL")
                else:
                    success, data = create_bookmark(token, title, url, tag_id)
                    if success:
                        st.success("Bookmark created! AI generated the summary.")
                        st.rerun()
                    else:
                        st.error("Failed to create bookmark.")

        st.divider()

        # Display Bookmarks Section
        st.subheader("Your Bookmarks")
        bookmarks = get_bookmarks(token)

        if not bookmarks:
            st.info("No bookmarks yet. Add one above!")
        else:
            # Use columns for a nicer layout
            for bm in bookmarks:
                with st.expander(f"🔖 {bm['title']}"):
                    st.markdown(f"**URL:** [{bm['url']}]({bm['url']})")
                    st.markdown(
                        f"**AI Summary:** {bm.get('notes', 'No summary available.')}"
                    )
                    tag_info = f"Tag ID: {bm.get('tag_id', 'None')}"
                    st.caption(
                        f"{tag_info} | Created: {bm.get('created_at', 'Unknown')}"
                    )


if __name__ == "__main__":
    main()
