from policyengine_us.model_api import *


class ok_federal_eitc_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC reduction for the Oklahoma EITC computation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        earnings = tax_unit("filer_adjusted_earnings", period)
        agi = tax_unit("adjusted_gross_income", period)
        highest_income_variable = max_(earnings, agi)
        phase_out_start = tax_unit("ok_federal_eitc_phase_out_start", period)
        phase_out_rate = tax_unit("ok_federal_eitc_phase_out_rate", period)
        phase_out_region = max_(0, highest_income_variable - phase_out_start)
        return phase_out_rate * phase_out_region
