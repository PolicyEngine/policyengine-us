from policyengine_us.model_api import *


class ga_tanf_family_maximum(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF family maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1525/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.financial_standards
        # In simplified implementation, use SPM unit size directly
        # (does not exclude SSI recipients from assistance unit)
        unit_size = spm_unit("spm_unit_size", period)

        # Maximum amounts for units up to max_table_size
        max_table_size = p.max_table_size
        capped_unit_size = min_(unit_size, max_table_size)
        max_amount = p.family_maximum.base[capped_unit_size]

        # Add increment for each additional person beyond max_table_size
        additional_members = max_(unit_size - max_table_size, 0)
        increment = additional_members * p.family_maximum.additional

        return max_amount + increment
