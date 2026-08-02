"""Portfolio analytics helpers."""


def calculate_return(initial_value: float, current_value: float) -> float:
    """Compute simple percentage return."""
    if initial_value == 0:
        return 0.0
    return ((current_value - initial_value) / initial_value) * 100
