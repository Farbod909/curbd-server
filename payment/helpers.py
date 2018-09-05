
def calculate_customer_price(pricing, minutes):
    pre_processing_fee_price = pricing * minutes / 60.0
    price = (pre_processing_fee_price + 30) * (1.0 / (1.0 - 0.029))
    return int(round(price))