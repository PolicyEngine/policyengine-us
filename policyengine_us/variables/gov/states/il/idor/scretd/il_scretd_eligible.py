from policyengine_us.model_api import *


class il_scretd_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Illinois Senior Citizens Real Estate Tax Deferral eligibility"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31"

    def formula(tax_unit, period, parameters):
        age_eligible = add(tax_unit, period, ["il_scretd_age_eligible"]) > 0
        income_eligible = tax_unit("il_scretd_income_eligible", period)
        return age_eligible & income_eligible
