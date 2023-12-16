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
        aged_head = tax_unit("age_head", period) >= p.aged_threshold
        aged_spouse = tax_unit("age_spouse", period) >= p.aged_threshold
        disabled_head = tax_unit("head_is_disabled", period)
        disabled_spouse = tax_unit("spouse_is_disabled", period)
        # if filing status is not joint, the disabled_exemption_spouse should be zero
        # The taxpayer shall not take additional exemptions with regard to spouse disability.
        joint_filing = (
            tax_unit("filing_status", period)
            == tax_unit("filing_status", period).possible_values.JOINT
        )
        head_exemption = max_(
            disabled_head * p.disabled, p.base * (1 + aged_head)
        )
        spouse_exemption = (
            max_(disabled_spouse * p.disabled, p.base * (1 + aged_spouse))
            * joint_filing
        )
        return where(
            (disabled_head + disabled_spouse * joint_filing) > 0,
            head_exemption + spouse_exemption,
            0,
        )
