import gurobipy as gp
from gurobipy import GRB

def run_sprint_optimization(df_tickets, dev_list):
    """
    Inputs:
    - df_tickets: The pandas DataFrame from your CSV
    - dev_list: The list of developers from st.session_state
    
    Returns:
    - A list of dictionaries containing ticket indices and assigned developers
    """
    # 1. Prepare Inputs
    tickets = df_tickets.index.tolist()
    developers = [dev['name'] for dev in dev_list]
    capacity = {dev['name']: dev['hours'] for dev in dev_list}
    
    # We use 'story_points' as the predicted time
    predicted_times = df_tickets['story_points'].fillna(0).tolist()

    # 2. Optimization Model
    m = gp.Model("Sprint_Planning")
    m.setParam('OutputFlag', 0)  # Silence Gurobi output for the web app

    # Decision variables
    x = m.addVars(tickets, developers, vtype=GRB.BINARY, name="assign")

    # Objective: Maximize total points assigned within capacity
    m.setObjective(
        gp.quicksum(predicted_times[i] * x[i, d] for i in tickets for d in developers),
        GRB.MAXIMIZE
    )

    # Constraints
    # Each ticket assigned to AT MOST one developer (some stay in backlog)
    for i in tickets:
        m.addConstr(gp.quicksum(x[i, d] for d in developers) <= 1)

    # Developer capacity constraints
    for d in developers:
        m.addConstr(
            gp.quicksum(predicted_times[i] * x[i, d] for i in tickets) <= capacity[d]
        )

    # 3. Solve
    m.optimize()

    # 4. Extract results
    assignment_results = []
    if m.Status == GRB.OPTIMAL:
        for i in tickets:
            for d in developers:
                if x[i, d].X > 0.5:
                    assignment_results.append({
                        "ticket_idx": i,
                        "developer": d
                    })
    
    return assignment_results