from policyengine_us.model_api import *


class mn_mfip_family_wage_level(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP Family Wage Level"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.02#stat.142G.02.42"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.17, Subd. 7:
        # Family Wage Level = 110% of Transitional Standard.
        # Used for both eligibility testing and benefit calculation.
        p = parameters(period).gov.states.mn.dcyf.mfip.income
        transitional_standard = spm_unit(
            "mn_mfip_transitional_standard", period
        )
        return transitional_standard * p.family_wage_level_multiplier
