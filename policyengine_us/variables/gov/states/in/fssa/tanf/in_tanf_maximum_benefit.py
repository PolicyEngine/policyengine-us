from policyengine_us.model_api import *


class in_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF maximum benefit amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-5",
        "https://www.in.gov/fssa/dfr/files/SNAP-TANF-Transmittal2024.pdf",
        "https://www.in.gov/fssa/dfr/files/3000.pdf#page=7",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.amount_of_assistance
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_table_size)
        additional_members = max_(size - p.max_table_size, 0)
        return p.amount[capped_size] + additional_members * p.additional_member_amount
