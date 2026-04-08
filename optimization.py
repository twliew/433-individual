from gurobipy import Model, GRB, quicksum

def run_sprint_optimization(df, developers, sprint_weeks=2):
    """
    ALL-OR-NOTHING assignment with Load Balancing:
    - Minimizes the maximum workload (L_max) across developers.
    - Ensures every ticket is assigned (or the model returns Infeasible).
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
        # T_i: Time required for ticket i
        T = {i: df.loc[i, 'time_to_resolution_hours'] for i in I}
        # C_d: Capacity for developer d
        C = {d: developers[d]['hours'] * sprint_weeks for d in D}

        # ----------------------------
        # Model
        # ----------------------------
        model = Model("Sprint_Optimization_Balanced")
        model.setParam("OutputFlag", 0)

        # Decision variables
        # x[i, d] = 1 if ticket i is assigned to developer d
        x = model.addVars(I, D, vtype=GRB.BINARY, name="x")
        
        # L_max represents the maximum workload assigned to any developer
        L_max = model.addVar(vtype=GRB.CONTINUOUS, name="L_max")

        # ----------------------------
        # Constraints
        # ----------------------------

        # 1. Assignment Constraint: Every ticket MUST be assigned to exactly one dev
        model.addConstrs(
            (quicksum(x[i, d] for d in D) == 1 for i in I),
            name="assign_all"
        )

        # 2. Hard Capacity: No developer can exceed their specific capacity
        model.addConstrs(
            (quicksum(T[i] * x[i, d] for i in I) <= C[d] for d in D),
            name="capacity"
        )

        # 3. Load Balancing: L_max must be >= the total hours of any developer
        model.addConstrs(
            (quicksum(T[i] * x[i, d] for i in I) <= L_max for d in D),
            name="define_lmax"
        )

        # ----------------------------
        # Objective: Minimize the bottleneck (L_max)
        # ----------------------------
        model.setObjective(L_max, GRB.MINIMIZE)

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

        # If the total hours required > total capacity, status will be INFEASIBLE
        elif model.status == GRB.INFEASIBLE:
            print("Infeasible: Total ticket hours exceed team capacity.")
            return []

        return []

    except Exception as e:
        print(f"Optimization Error: {e}")
        return []