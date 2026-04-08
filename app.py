import pandas as pd
import streamlit as st
from optimization import run_sprint_optimization

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="Ticket Assignment Board", layout="wide")

# Initialize Session State
if 'sprint_number' not in st.session_state:
    st.session_state.sprint_number = 1
if 'developers' not in st.session_state:
    st.session_state.developers = [{"name": "Developer 1", "hours": 50}]
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
        
        df['time_to_resolution_hours'] = pd.to_numeric(
            df['time_to_resolution_hours'], errors='coerce'
        ).fillna(0)
        
        target_sprint = f"Sprint {current_sprint_number}"
        sprint_df = df[df['sprint'].astype(str).str.strip() == target_sprint].copy()
        
        sprint_df = sprint_df[sprint_df['time_to_resolution_hours'] < 60].copy()
        
        return sprint_df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "issue_key", "description", "priority", "sprint", "time_to_resolution_hours"
        ])

df_backlog = load_and_filter_data(st.session_state.sprint_number)

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title(f"Current Sprint: {st.session_state.sprint_number}")

if st.sidebar.button("Complete Sprint", use_container_width=True):
    for item in st.session_state.sprint_assignments:
        item['completed_in'] = f"Sprint {st.session_state.sprint_number}"
    st.session_state.done_tickets.extend(st.session_state.sprint_assignments)
    st.session_state.sprint_assignments = []
    st.session_state.selected_tickets = set()
    st.session_state.sprint_number += 1
    st.rerun()

if st.sidebar.button("⚡ Optimize Selected", type="primary", use_container_width=True):
    if not st.session_state.selected_tickets:
        st.sidebar.error("Select tickets from Backlog first!")
    else:
        df_to_opt = df_backlog.loc[list(st.session_state.selected_tickets)]
        results = run_sprint_optimization(df_to_opt, st.session_state.developers)
        
        if results:
            st.session_state.sprint_assignments.extend(results)
            st.session_state.selected_tickets = set()
            st.rerun()
        else:
            st.session_state.selected_tickets = set()
            st.sidebar.error("Optimization failed! Check team capacity.")

# ----------------------------
# Team Section
# ----------------------------
st.sidebar.divider()
st.sidebar.title("Team Capacity")

if st.sidebar.button("➕ Add Developer"):
    st.session_state.developers.append({
        "name": f"Developer {len(st.session_state.developers)+1}",
        "hours": 50 
    })

for i, dev in enumerate(st.session_state.developers):
    with st.sidebar.container(border=True):
        cols = st.columns([4, 1])
        
        with cols[1]:
            # Guard: Protect Developer 1 from deletion
            if i > 0: 
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.developers.pop(i)
                    st.rerun()
            else:
                st.write("") 

        st.session_state.developers[i]['name'] = st.text_input(
            "Name", 
            value=dev['name'], 
            key=f"n_{i}"
        )
        
        st.session_state.developers[i]['hours'] = st.number_input(
            "Weekly Hours", 
            min_value=0, 
            max_value=168, 
            value=dev['hours'], 
            key=f"h_{i}"
        )

# ----------------------------
# Main Dashboard
# ----------------------------
st.title("Ticket Assignment Board")
col_backlog, col_sprint, col_done = st.columns(3)

assigned_ids = [item['ticket_idx'] for item in st.session_state.sprint_assignments]
done_ids = [item['ticket_idx'] for item in st.session_state.done_tickets]

# ----------------------------
# Backlog
# ----------------------------
with col_backlog:
    st.header("📋 Backlog")
    st.divider()

    if df_backlog.empty:
        st.write("No tickets for this sprint.")

    for index, row in df_backlog.iterrows():
        if index not in assigned_ids and index not in done_ids:
            with st.container(border=True):
                is_selected = st.checkbox(
                    f"**{row['issue_key']}**",
                    key=f"check_{index}",
                    value=index in st.session_state.selected_tickets
                )

                if is_selected:
                    st.session_state.selected_tickets.add(index)
                else:
                    st.session_state.selected_tickets.discard(index)

                st.write(row['description'])
                st.info(f"⏱️ Estimate: {round(row['time_to_resolution_hours'], 1)}h")

# ----------------------------
# Assignments
# ----------------------------
with col_sprint:
    st.header("👤 Assignments")
    st.divider()

    for item in st.session_state.sprint_assignments:
        with st.container(border=True):
            st.subheader(item['issue_key'])
            # Removed curly braces to show clean text
            st.success(item['developer'])
            st.write(f"Assigned Time: {round(item['time_to_resolution_hours'], 1)}h")

# ----------------------------
# Completed
# ----------------------------
with col_done:
    st.header("✅ Completed")
    st.divider()

    for item in reversed(st.session_state.done_tickets):
        with st.container(border=True):
            st.caption(f"🏁 {item.get('completed_in', 'Done')}")
            # Removed curly braces to show clean text
            st.write(item['issue_key'])
            st.caption(
                f"Dev: {item['developer']} "
                f"({round(item['time_to_resolution_hours'], 1)}h)"
            )