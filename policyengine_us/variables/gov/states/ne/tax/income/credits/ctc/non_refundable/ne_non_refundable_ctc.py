from policyengine_us.model_api import *


class ne_non_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.tax.income.credits.ctc.non_refundable
        total_contributions = tax_unit(
            "ne_qualifying_contributions_to_eligible_program", period
        )
        opportunity_zone_contributions = tax_unit(
            "ne_qualifying_contributions_to_eligible_program_with_physical_presence_in_opportunity_zone",
            period,
        )
        child_care_contributions = tax_unit(
            "ne_qualifying_contributions_to_eligible_child_care_subsidy_program",
            period,
        )
        max_rate_eligible = (opportunity_zone_contributions > 0) & (
            child_care_contributions > 0
        )
        credit_amount = total_contributions * where(
            max_rate_eligible, p.max_fraction, p.min_fraction
        )
        return min_(credit_amount, p.cap)
