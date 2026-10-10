from policyengine_us.model_api import *


class va_national_guard_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia national guard pay subtraction"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.national_guard_pay
        national_guard_pay = add(tax_unit, period, ["military_service_income"])
        # A filer who forgoes the subtraction to claim the low-income credit
        # or EITC gets none (Va. Code 58.1-339.8(D)(1)).
        claimed = tax_unit("va_claims_eitc_disqualifying_benefits", period)
        return claimed * min_(national_guard_pay, p.cap)
