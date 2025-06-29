from math import pow

def run_loan_calc(principal: float, annual_rate: float = 9.0, years: int = 20) -> dict:
    """
    Compute EMI and total payment based on principal, annual_rate (in %), and tenure (years).
    Returns:
      {
        "emi": <monthly payment>,
        "total_payment": <emi * total months>
      }
    """
    r = annual_rate / (12 * 100)
    n = years * 12
    emi = (principal * r * pow(1 + r, n)) / (pow(1 + r, n) - 1)
    return {
        "emi": round(emi, 2),
        "total_payment": round(emi * n, 2)
    }
