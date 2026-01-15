from policyengine_us.model_api import *


class il_scretd_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Illinois Senior Citizens Real Estate Tax Deferral income eligibility"
    )
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.idor.scretd
        income = add(tax_unit, period, ["irs_gross_income"])
        return income <= p.income_limit
