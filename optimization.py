from gurobipy import Model, GRB, quicksum

def run_sprint_optimization(df, developers, sprint_weeks=2):
    """
    ALL-OR-NOTHING assignment:
    - Either all selected tickets are assigned
    - Or none are assigned (fail)
    """
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
        C = {d: developers[d]['hours'] * sprint_weeks for d in D}

        # ----------------------------
        # Model
        # ----------------------------
        model = Model("Sprint_Optimization")
        model.setParam("OutputFlag", 0)

        # Decision variables
        x = model.addVars(I, D, vtype=GRB.BINARY, name="x")

        # ----------------------------
        # Constraints
        # ----------------------------

        # 🔥 KEY FIX: every ticket MUST be assigned
        model.addConstrs(
            (quicksum(x[i, d] for d in D) == 1 for i in I),
            name="assign_all"
        )

        # Capacity constraints
        model.addConstrs(
            (quicksum(T[i] * x[i, d] for i in I) <= C[d] for d in D),
            name="capacity"
        )

        # Dummy objective (feasibility problem)
        model.setObjective(0, GRB.MAXIMIZE)

        # ----------------------------
        # Solve
        # ----------------------------
        model.optimize()

        # ----------------------------
        # Results
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
                            "description": df.loc[i, "description"]
                            if "description" in df.columns else ""
                        })
            return results

        # 🔥 If infeasible → return empty (triggers error in UI)
        elif model.status == GRB.INFEASIBLE:
            return []

        return []

    except Exception as e:
        print(f"Optimization Error: {e}")
        return []