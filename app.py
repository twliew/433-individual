import pandas as pd
import streamlit as st

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="Ticket Board", layout="wide")

st.title("Ticket Board")

# Initialize the sprint number in session state if it doesn't exist
if 'sprint_number' not in st.session_state:
    st.session_state.sprint_number = 1

# ----------------------------
# Sidebar: Sprint Control & Developer Management
# ----------------------------
st.sidebar.title("Workforce Planner")

# 1. Sprint Display (Small & Clean)
st.sidebar.markdown(f"### 🚀 Sprint: {st.session_state.sprint_number}")

if st.sidebar.button("Optimize"):
    #TODO: connect to optimization algorithm
    st.sidebar.success("Optimization algorithm executed!")

# 2. Next Sprint Button (Standard size, at the top)
if st.sidebar.button("Next Sprint >>"):
    st.session_state.sprint_number += 1
    # TODO: Logic to move Sprint tickets to Done
    st.rerun()

st.sidebar.divider()

# 3. Developer Management (Existing code below the sprint controls)
st.sidebar.header("Team Capacity")

# Initialize developer list in session state
if 'developers' not in st.session_state:
    st.session_state.developers = [{"name": "Taylor", "hours": 40}]

# --- Callback Functions ---
def add_developer():
    new_index = len(st.session_state.developers) + 1
    st.session_state.developers.append({"name": f"Developer {new_index}", "hours": 40})

def remove_specific_developer(index):
    # Ensure at least one developer remains
    if len(st.session_state.developers) > 1:
        st.session_state.developers.pop(index)
    else:
        st.sidebar.warning("You must have at least one developer.")

# --- Sidebar UI ---
if st.sidebar.button("➕ Add Developer", use_container_width=True):
    add_developer()

st.sidebar.divider()

# Loop through developers and create a "card" for each
for i, dev in enumerate(st.session_state.developers):
    with st.sidebar.container(border=True):
        # Header with Name and a Trash/Remove button on the same line
        col_header, col_del = st.columns([4, 1])
        with col_header:
            st.markdown(f"**{dev['name']}**")
        with col_del:
            # We use a unique key for every button and the callback to delete this specific index
            if st.button("X", key=f"del_{i}", help="Remove this developer"):
                remove_specific_developer(i)
                st.rerun()

        # Input fields
        st.session_state.developers[i]['name'] = st.text_input(
            "Name", value=dev['name'], key=f"name_input_{i}", label_visibility="collapsed"
        )
        st.session_state.developers[i]['hours'] = st.number_input(
            "Hours", value=dev['hours'], min_value=0, max_value=100, key=f"hrs_input_{i}"
        )

# Calculate total capacity
total_capacity = sum(dev['hours'] for dev in st.session_state.developers)
st.sidebar.metric("Total Team Capacity", f"{total_capacity} hrs")


# ----------------------------
# Optimize Button
# ----------------------------
# TODO: run optimization algorithm

# ----------------------------
# Load Data
# ----------------------------
def load_data():
    try:
        df = pd.read_csv('jira_m2_accelerated.csv', nrows=10)
        return df
    except FileNotFoundError:
        # Match the schema you expect from your CSV
        return pd.DataFrame(columns=["issue_key", "issue_type", "story_points", "priority", "description"])

df_tickets = load_data()

# ----------------------------
# Create Columns
# ----------------------------
col_backlog, col_sprint, col_done = st.columns(3)

with col_backlog:
    st.header("Backlog")
    st.divider()
    
    if df_tickets.empty:
        st.info("There are currently no tickets in the backlog")
    else:
        for index, row in df_tickets.iterrows():
            with st.container(border=True):
                # Using 'issue_key' as the header and 'description' as the body
                st.subheader(f"Ticket: {row['issue_key']}")
                
                # Use .get() or check column names to avoid future KeyErrors
                st.write(row['description'])
                
                # Metadata row
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Type: {row['issue_type']}")
                with col2:
                    st.caption(f"Story Points: {row['story_points']}")
                
                st.caption(f"Priority: {row['priority']}")

with col_sprint:
    st.header("Sprint")
    st.divider()

with col_done:
    st.header("Done")
    st.divider()