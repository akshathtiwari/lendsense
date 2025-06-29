def check_eligibility(net_salary: float, emi: float, ltv: float) -> dict:
    """
    FOIR <= 40 %  and  LTV <= 80 %.
    Accepts ltv as fraction (0.70) or percentage (70 / 70.0).
    """
    # Normalise LTV
    ltv_fraction = ltv / 100 if ltv > 1 else ltv

    foir_ok = emi <= 0.40 * net_salary
    ltv_ok  = ltv_fraction <= 0.80
    return {
        "foir_ok": foir_ok,
        "ltv_ok":  ltv_ok,
        "eligible": foir_ok and ltv_ok
    }