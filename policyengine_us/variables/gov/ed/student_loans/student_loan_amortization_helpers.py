from policyengine_us.model_api import *


def amortized_monthly_payment(balance, annual_rate, number_of_payments):
    """Level monthly payment that repays `balance` in `number_of_payments`
    months at `annual_rate`, compounded monthly.

    The payment is balance x i / (1 - (1 + i) ^ -n), where i is the annual
    rate divided by 12 and n is the number of payments, or balance / n at a
    zero rate. `number_of_payments` can be a scalar or an array.
    """
    monthly_rate = annual_rate / MONTHS_IN_YEAR
    discount = 1 - (1 + monthly_rate) ** -number_of_payments
    payment_per_dollar = np.divide(
        monthly_rate,
        discount,
        out=np.ones_like(monthly_rate) / number_of_payments,
        where=monthly_rate > 0,
    )
    return balance * payment_per_dollar
