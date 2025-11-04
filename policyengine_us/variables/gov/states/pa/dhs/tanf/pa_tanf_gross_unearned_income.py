from policyengine_us.model_api import *


class pa_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Section 183.31 - Unearned income"
    documentation = "Gross unearned income including benefits, dividends, interest, child support, and cash contributions, before any deductions or exclusions. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.31.html"

    adds = "gov.hhs.tanf.cash.income.sources.unearned"
