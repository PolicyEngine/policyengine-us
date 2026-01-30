from policyengine_us.model_api import *


class ri_works_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island Works payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
        "https://dhs.ri.gov/press-releases/rhode-island-works-families-see-increase-benefits-fy-2025-state-budget",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.works
        unit_size = spm_unit("spm_unit_size", period)
        max_table_size = p.payment_standard.max_unit_size
        capped_size = min_(unit_size, max_table_size)
        base_amount = p.payment_standard.amount[capped_size]

        # Add additional amount per person beyond max table size
        additional_persons = max_(unit_size - max_table_size, 0)
        additional_amount = (
            additional_persons * p.payment_standard.additional_person
        )

        standard = base_amount + additional_amount

        # Apply subsidized housing reduction
        receives_housing = spm_unit(
            "receives_housing_assistance", period.this_year
        )
        housing_reduction = where(
            receives_housing, p.subsidized_housing_reduction, 0
        )

        return max_(standard - housing_reduction, 0)
