from policyengine_us.model_api import *


class hi_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Hawaii TANF gross income eligibility"
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=19",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf

        gross_income = spm_unit("hi_tanf_gross_income", period)

        # Gross income limit = 185% of Standard of Need
        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_unit_size)
        standard_of_need = p.standard_of_need.amount[capped_size]
        gross_income_limit = (
            standard_of_need * p.eligibility.gross_income_limit_rate
        )

        return gross_income <= gross_income_limit
