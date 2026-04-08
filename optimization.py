from gurobipy import Model, GRB, quicksum

def run_sprint_optimization(df, developers):
    try:
        # ----------------------------
        # Sets & Indices
        # ----------------------------
        I = list(df.index)  # tickets
        D = list(range(len(developers)))  # developers (indexed)

        # ----------------------------
        # Parameters
        # ----------------------------
        P = {i: df.loc[i, 'story_points'] for i in I}  # story points
        C = {d: developers[d]['hours'] for d in D}     # capacity

        # ----------------------------
        # Model
        # ----------------------------
        model = Model("Sprint_Optimization")
        model.setParam("OutputFlag", 0)  # silence output

        # ----------------------------
        # Decision Variables
        # x[i,d] = 1 if ticket i assigned to developer d
        # ----------------------------
        x = model.addVars(I, D, vtype=GRB.BINARY, name="x")

        # ----------------------------
        # Objective Function
        # Maximize total story points assigned
        # ----------------------------
        model.setObjective(
            quicksum(P[i] * x[i, d] for i in I for d in D),
            GRB.MAXIMIZE
        )

        # ----------------------------
        # Constraints
        # ----------------------------

        # 1. Each ticket assigned to at most one developer
        for i in I:
            model.addConstr(
                quicksum(x[i, d] for d in D) <= 1,
                name=f"assign_once_{i}"
            )

        # 2. Developer capacity constraints
        for d in D:
            model.addConstr(
                quicksum(P[i] * x[i, d] for i in I) <= C[d],
                name=f"capacity_{d}"
            )

        # ----------------------------
        # Solve
        # ----------------------------
        model.optimize()

        # ----------------------------
        # Extract Results
        # ----------------------------
        if model.status == GRB.OPTIMAL:
            results = []

            for i in I:
                for d in D:
                    if x[i, d].X > 0.5:
                        results.append({
                            "ticket_idx": i,
                            "developer": developers[d]["name"],
                            "story_points": P[i],
                            "issue_key": df.loc[i, "issue_key"]
                        })

            return results
        else:
            return None

    except Exception as e:
        print(f"Optimization Error: {e}")
        return None