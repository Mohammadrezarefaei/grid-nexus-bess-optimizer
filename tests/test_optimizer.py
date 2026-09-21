import pytest
import pulp

def test_pulp_solver_availability():
    """Verify that the PuLP solver is available and working correctly."""
    model = pulp.LpProblem("Test_Model", pulp.LpMaximize)
    x = pulp.LpVariable("x", lowBound=0, upBound=10)
    model += x
    model += (x <= 5)
    status = model.solve(pulp.PULP_CBC_CMD(msg=0))
    assert pulp.LpStatus[status] == "Optimal"
    assert x.varValue == 5.0
