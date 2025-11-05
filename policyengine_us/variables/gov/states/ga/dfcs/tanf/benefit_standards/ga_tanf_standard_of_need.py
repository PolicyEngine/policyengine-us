from policyengine_us.model_api import *


class ga_tanf_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF standard of need"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1525/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.benefit_standards
        unit_size = spm_unit("ga_tanf_assistance_unit_size", period)

        # Standard amounts for units up to 10 people
        standard_amount = p.standard_of_need[
            min_(unit_size, len(p.standard_of_need.keys()))
        ]

        # Add increment for each additional person beyond 10
        max_table_size = len(p.standard_of_need.keys())
        additional_members = max_(unit_size - max_table_size, 0)
        increment = additional_members * p.standard_of_need_increment

        return standard_amount + increment
