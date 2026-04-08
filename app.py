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
# Data Loading & Filtering
# ----------------------------
@st.cache_data
def load_and_filter_data(current_sprint_number):
    try:
        df = pd.read_csv('predictions.csv')
        
        # Ensure story_points is numeric for the optimizer
        df['story_points'] = pd.to_numeric(df['story_points'], errors='coerce').fillna(0)
        
        # Create the string to match your CSV format (e.g., "Sprint 1")
        target_sprint = f"Sprint {current_sprint_number}"
        
        # Filter the dataframe
        # .str.strip() ensures we match even if there are hidden spaces
        sprint_df = df[df['sprint'].astype(str).str.strip() == target_sprint].copy()
        
        return sprint_df
    except FileNotFoundError:
        return pd.DataFrame(columns=["issue_key", "description", "story_points", "priority", "sprint"])

# Load data based on the numeric sprint state
df_backlog = load_and_filter_data(st.session_state.sprint_number)

# ----------------------------
# Sidebar: Controls & Team
# ----------------------------
st.sidebar.title("Settings")
st.sidebar.markdown(f"### 🚀 Current Sprint: {st.session_state.sprint_number}")

# Next Sprint Button
if st.sidebar.button("Complete Sprint", use_container_width=True):
    # 1. Move current active assignments to the "Done" list
    st.session_state.done_tickets.extend(st.session_state.sprint_assignments)
    # 2. Clear current sprint workspace
    st.session_state.sprint_assignments = []
    st.session_state.selected_tickets = set()
    # 3. Increment sprint
    st.session_state.sprint_number += 1
    st.rerun()


# Optimize Button
if st.sidebar.button("⚡ Optimize Selected", type="primary", use_container_width=True):
    if not st.session_state.selected_tickets:
        st.sidebar.error("Select tickets from Backlog first!")
    else:
        # Pass only the selected rows from the filtered backlog to the optimizer
        df_to_opt = df_backlog.loc[list(st.session_state.selected_tickets)]
        results = run_sprint_optimization(df_to_opt, st.session_state.developers)
        
        if results:
            st.session_state.sprint_assignments.extend(results)
            st.session_state.selected_tickets = set() 
            st.rerun()
        else:
            st.sidebar.error("Optimization failed! Check capacity.")

st.sidebar.divider()

# Developer Management
st.sidebar.header("Team Capacity")

if st.sidebar.button("➕ Add Developer"):
    idx = len(st.session_state.developers) + 1
    st.session_state.developers.append({"name": f"Developer {idx}", "hours": 40})

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


# ----------------------------
# Main Dashboard
# ----------------------------
st.title("Ticket Assignment Board")

col_backlog, col_sprint, col_done = st.columns(3)

# Filter out tickets that are already assigned or done
assigned_ids = [item['ticket_idx'] for item in st.session_state.sprint_assignments]
done_ids = [item['ticket_idx'] for item in st.session_state.done_tickets]

with col_backlog:
    st.header(f"Sprint {st.session_state.sprint_number} Backlog")
    st.divider()
    
    if df_backlog.empty:
        st.write("No tickets found for this sprint.")
    
    for index, row in df_backlog.iterrows():
        # Only show if it hasn't been moved to Sprint or Done yet
        if index not in assigned_ids and index not in done_ids:
            with st.container(border=True):
                is_selected = index in st.session_state.selected_tickets
                select = st.checkbox(f"**{row['issue_key']}**", value=is_selected, key=f"check_{index}")
                
                if select:
                    st.session_state.selected_tickets.add(index)
                else:
                    st.session_state.selected_tickets.discard(index)
                
                st.write(row['description'])
                st.caption(f"Pts: {row['story_points']} | Priority: {row['priority']}")

with col_sprint:
    st.header("Ticket Assignments")
    st.divider()
    for item in st.session_state.sprint_assignments:
        # Note: We use df_backlog here since it contains the current sprint's data
        ticket = df_backlog.loc[item['ticket_idx']]
        with st.container(border=True):
            st.subheader(ticket['issue_key'])
            st.success(f"👤 {item['developer']}")
            st.write(ticket['description'])

with col_done:
    st.header("Completed")
    st.divider()
    # For "Done", we need to be careful as these might be from previous sprints.
    # If the app slows down here, you can limit this list to the last 20 items.
    for item in reversed(st.session_state.done_tickets):
        # Using a safer lookup in case the index is from a different dataframe slice
        try:
            # Re-loading full data for 'Done' column lookups is slow, 
            # ideally 'done_tickets' should store the ticket info directly.
            # For now, this assumes the index exists in the global dataset.
            ticket_key = item.get('issue_key', f"Index {item['ticket_idx']}")
            with st.container(border=True):
                st.write(f"✅ **{ticket_key}**")
                st.caption(f"Done by: {item['developer']}")
        except:
            continue