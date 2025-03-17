from policyengine_us.model_api import *


class ma_tafdc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        eligible_children = (
            spm_unit.sum(spm_unit.members("ma_tafdc_eligible_child", period))
            > 0
        )
        pregnancy_eligible = spm_unit("ma_tafdc_pregnancy_eligible", period)
        income_eligible = spm_unit("ma_tafdc_income_eligible", period)
        immigration_eligible = spm_unit(
            "ma_tafdc_immigration_status_eligible", period
        )
        return (
            (eligible_children | pregnancy_eligible)
            & income_eligible
            & immigration_eligible
        )
