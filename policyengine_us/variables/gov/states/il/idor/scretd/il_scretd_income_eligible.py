from policyengine_us.model_api import *


class il_scretd_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Illinois Senior Citizens Real Estate Tax Deferral income eligibility"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31",
        # 320 ILCS 30/2(a)(iii) and (j): household income no greater than the
        # maximum household income.
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/032000300K2.htm",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.idor.scretd
        income = tax_unit("il_scretd_household_income", period)
        return income <= p.income_limit
