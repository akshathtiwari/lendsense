def check_eligibility(net_salary: float, emi: float, ltv: float) -> dict:
    """
    Simple FOIR rule:
      • EMI must be ≤ 40% of net_salary
      • LTV must be ≤ 80%
    Returns:
      {
        "foir_ok": bool,
        "ltv_ok": bool,
        "eligible": bool
      }
    """
    foir_ok = emi <= 0.4 * net_salary
    ltv_ok = ltv <= 0.80
    return {
        "foir_ok": foir_ok,
        "ltv_ok": ltv_ok,
        "eligible": foir_ok and ltv_ok
    }
