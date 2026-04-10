from gurobipy import Model, GRB, quicksum

def run_sprint_optimization(df, developers, sprint_weeks=2):
    try:
        if df.empty:
            return []

        # ----------------------------
        # Sets
        # ----------------------------
        I = list(df.index)
        D = list(range(len(developers)))

        # ----------------------------
        # Parameters
        # ----------------------------
        T = {i: df.loc[i, 'time_to_resolution_hours'] for i in I}
        
        # C_d: Capacity = Weekly hours * number of weeks in the sprint
        C = {d: developers[d]['hours'] * sprint_weeks for d in D}

        # ----------------------------
        # Model Setup
        # ----------------------------
        model = Model("Sprint_Optimization_Balanced")
        model.setParam("OutputFlag", 0)

        # ----------------------------
        # Decision Variables
        # ----------------------------
        x = model.addVars(I, D, vtype=GRB.BINARY, name="x")
        L_max = model.addVar(vtype=GRB.CONTINUOUS, name="L_max")

        # ----------------------------
        # Constraints
        # ----------------------------

        # 1. Assignment: Every selected ticket must be assigned to exactly one dev
        model.addConstrs(
            (quicksum(x[i, d] for d in D) == 1 for i in I),
            name="assign_all"
        )

        # 2. Hard Capacity: Sum of tickets per dev <= Weekly capacity * weeks
        model.addConstrs(
            (quicksum(T[i] * x[i, d] for i in I) <= C[d] for d in D),
            name="capacity"
        )

        # 3. Load Balancing: L_max is the ceiling for all developer loads
        model.addConstrs(
            (quicksum(T[i] * x[i, d] for i in I) <= L_max for d in D),
            name="define_lmax"
        )

        # ----------------------------
        # Objective & Solve
        # ----------------------------
        model.setObjective(L_max, GRB.MINIMIZE)
        model.optimize()

        # ----------------------------
        # Results Parsing
        # ----------------------------
        if model.status == GRB.OPTIMAL:
            results = []
            for i in I:
                for d in D:
                    if x[i, d].X > 0.5:
                        results.append({
                            "ticket_idx": i,
                            "developer": developers[d]["name"],
                            "time_to_resolution_hours": T[i],
                            "issue_key": df.loc[i, "issue_key"],
                            "description": df.loc[i, "description"] if "description" in df.columns else ""
                        })
            return results

        return []

    except Exception as e:
        print(f"Optimization Error: {e}")
        return []