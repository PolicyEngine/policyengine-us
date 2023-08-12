from policyengine_us.model_api import *


class tax_exempt_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt dividend income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.investopedia.com/terms/e/exempt-interest-dividend.asp"
        "https://www.investopedia.com/ask/answers/090415/dividend-income-taxable.asp#:~:text=How%20Do%20I%20Avoid%20Paying%20Taxes%20on%20Dividends"
    )
