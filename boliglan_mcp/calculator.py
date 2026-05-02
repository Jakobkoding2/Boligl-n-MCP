"""Mortgage savings calculator using standard annuity formula."""


def calculate_savings(
    loan_amount: int,
    current_rate: float,
    new_rate: float,
    years: int = 5,
    remaining_term_years: int = 25,
) -> dict:
    """
    Calculate monthly and total payment savings when the interest rate changes.

    Returns a dict with keys: monthly, yearly, total, total_interest_savings,
    current_monthly, new_monthly, rate_diff.
    """
    months_total = remaining_term_years * 12
    calc_months = years * 12

    r_cur = current_rate / 100 / 12
    r_new = new_rate / 100 / 12

    def annuity(principal: int, monthly_rate: float, n: int) -> float:
        if monthly_rate == 0:
            return principal / n
        return principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)

    current_monthly = annuity(loan_amount, r_cur, months_total)
    new_monthly = annuity(loan_amount, r_new, months_total)
    monthly_diff = current_monthly - new_monthly

    total_interest_current = current_monthly * months_total - loan_amount
    total_interest_new = new_monthly * months_total - loan_amount

    return {
        "monthly": round(monthly_diff),
        "yearly": round(monthly_diff * 12),
        "total": round(monthly_diff * calc_months),
        "total_interest_savings": round(total_interest_current - total_interest_new),
        "current_monthly": round(current_monthly),
        "new_monthly": round(new_monthly),
        "rate_diff": round(current_rate - new_rate, 2),
    }
