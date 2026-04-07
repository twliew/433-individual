import pandas as pd
import streamlit as st
from optimization import run_sprint_optimization

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="Workforce Planner", layout="wide")

# Initialize Session State
if 'sprint_number' not in st.session_state:
    st.session_state.sprint_number = 1
if 'developers' not in st.session_state:
    st.session_state.developers = [{"name": "Developer 1", "hours": 40}]
if 'sprint_assignments' not in st.session_state:
    st.session_state.sprint_assignments = []
if 'done_tickets' not in st.session_state:
    st.session_state.done_tickets = []
if 'selected_tickets' not in st.session_state:
    st.session_state.selected_tickets = set()

# ----------------------------
# Data Loading
# ----------------------------
@st.cache_data
def load_data():
    try:
        # Loading your specific Jira file
        df = pd.read_csv('jira_m2_accelerated.csv')
        # Ensure story_points is numeric
        df['story_points'] = pd.to_numeric(df['story_points'], errors='coerce').fillna(0)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["issue_key", "description", "story_points", "priority", "issue_type"])

df_tickets = load_data()

# ----------------------------
# Sidebar: Controls & Team
# ----------------------------
st.sidebar.title("Settings")
st.sidebar.markdown(f"### 🚀 Sprint: {st.session_state.sprint_number}")

# Next Sprint Button
if st.sidebar.button("Next Sprint >>", use_container_width=True):
    # Move current assignments to Done
    st.session_state.done_tickets.extend(st.session_state.sprint_assignments)
    st.session_state.sprint_assignments = []
    st.session_state.sprint_number += 1
    st.rerun()

st.sidebar.divider()

# Developer Management
st.sidebar.header("Team Capacity")

def add_dev():
    idx = len(st.session_state.developers) + 1
    st.session_state.developers.append({"name": f"Developer {idx}", "hours": 40})

if st.sidebar.button("➕ Add Developer"):
    add_dev()

for i, dev in enumerate(st.session_state.developers):
    with st.sidebar.container(border=True):
        cols = st.columns([4, 1])
        with cols[1]:
            if st.button("🗑️", key=f"del_{i}"):
                if len(st.session_state.developers) > 1:
                    st.session_state.developers.pop(i)
                    st.rerun()
        
        st.session_state.developers[i]['name'] = st.text_input("Name", value=dev['name'], key=f"n_{i}")
        st.session_state.developers[i]['hours'] = st.number_input("Hours", value=dev['hours'], key=f"h_{i}")

st.sidebar.divider()

# Optimize Button
if st.sidebar.button("⚡ Optimize Selected", type="primary", use_container_width=True):
    if not st.session_state.selected_tickets:
        st.sidebar.error("Select tickets from Backlog first!")
    else:
        selected_indices = list(st.session_state.selected_tickets)
        df_to_opt = df_tickets.loc[selected_indices]
        
        results = run_sprint_optimization(df_to_opt, st.session_state.developers)
        
        if results:
            st.session_state.sprint_assignments.extend(results)
            st.session_state.selected_tickets = set() # Clear selection
            st.rerun()
        else:
            st.sidebar.error("Optimization failed! Check if total hours are sufficient.")

# ----------------------------
# Main Dashboard
# ----------------------------
st.title("Workforce Ticket Board")

col_backlog, col_sprint, col_done = st.columns(3)

# Track what is already "out" of the backlog
assigned_ids = [item['ticket_idx'] for item in st.session_state.sprint_assignments]
done_ids = [item['ticket_idx'] for item in st.session_state.done_tickets]

with col_backlog:
    st.header("Backlog")
    st.divider()
    for index, row in df_tickets.iterrows():
        if index not in assigned_ids and index not in done_ids:
            with st.container(border=True):
                # Using a checkbox to add/remove from selection set
                select = st.checkbox(f"**{row['issue_key']}**", key=f"check_{index}")
                if select:
                    st.session_state.selected_tickets.add(index)
                else:
                    st.session_state.selected_tickets.discard(index)
                
                st.write(row['description'])
                st.caption(f"Points: {row['story_points']} | Priority: {row['priority']}")

with col_sprint:
    st.header("Sprint")
    st.divider()
    for item in st.session_state.sprint_assignments:
        ticket = df_tickets.loc[item['ticket_idx']]
        with st.container(border=True):
            st.subheader(ticket['issue_key'])
            st.info(f"👤 Assigned: {item['developer']}")
            st.write(ticket['description'])

with col_done:
    st.header("Done")
    st.divider()
    for item in st.session_state.done_tickets:
        ticket = df_tickets.loc[item['ticket_idx']]
        with st.container(border=True):
            st.write(f"✅ **{ticket['issue_key']}**")
            st.caption(f"Completed by: {item['developer']}")