from policyengine_us.model_api import *


class hi_disabled_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii disabled exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.exemptions
        aged_head = (tax_unit("age_head", period) >= p.aged_threshold).astype(
            int
        )
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.aged_threshold
        ).astype(int)
        disabled_head = tax_unit("head_is_disabled", period).astype(int)
        disabled_spouse = tax_unit("spouse_is_disabled", period).astype(int)
        non_disabled_head = p.base * (1 + aged_head)
        non_disabled_spouse = p.base * (1 + aged_spouse)
        disabled_exemption_head = where(
            disabled_head,
            max(disabled_head * p.disabled, non_disabled_head),
            non_disabled_head,
        )
        # if filing status is not joint, the disabled_exemption_spouse should be zero
        # The taxpayer shall not take additional exemptions with regard to spouse disability
        joint_filing_status = (
            tax_unit("filing_status", period)
            == tax_unit("filing_status", period).possible_values.JOINT
        )
        disabled_exemption_spouse = (
            where(
                disabled_spouse,
                max(disabled_spouse * p.disabled, non_disabled_spouse),
                non_disabled_spouse,
            )
            * joint_filing_status
        )

        return where(
            (disabled_head + disabled_spouse * joint_filing_status) > 0,
            disabled_exemption_head + disabled_exemption_spouse,
            0,
        )
