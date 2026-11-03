CURRENCY_SYMBOL = "₱"

def money(amount: float):
    return f"{CURRENCY_SYMBOL}{amount:.2f}"