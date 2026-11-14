from policyengine_us.model_api import *


class mn_homestead_credit_refund_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Minnesota Homestead Credit Refund"
    definition_period = YEAR
    reference = (
        "https://www.taxformfinder.org/forms/2024/2024-minnesota-form-m1pr-instructions.pdf#page=2",
        "https://www.taxformfinder.org/forms/2025/2025-minnesota-form-m1pr-instructions.pdf#page=2",
        # PDF pages 5, 9
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=5",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.property.homestead_credit_refund
        household_income = tax_unit(
            "mn_homestead_credit_refund_household_income", period
        )
        property_tax = add(tax_unit, period, ["real_estate_taxes"])

        claimants = tax_unit.members("is_tax_unit_head_or_spouse", period)
        claimant_is_tax_unit_dependent = tax_unit.any(
            claimants & tax_unit.members("is_tax_unit_dependent", period)
        )
        claimant_is_dependent_elsewhere = tax_unit(
            "head_is_dependent_elsewhere", period
        ) | tax_unit("spouse_is_dependent_elsewhere", period)
        claimant_is_dependent = (
            claimant_is_tax_unit_dependent | claimant_is_dependent_elsewhere
        )

        return (
            (property_tax > 0)
            & ~claimant_is_dependent
            & (p.max_refund.calc(household_income) > 0)
        )

    def formula_2025(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.property.homestead_credit_refund
        household_income = np.floor(
            max_(tax_unit("mn_homestead_credit_refund_household_income", period), 0)
            + 0.5
        )
        property_tax = tax_unit(
            "mn_homestead_credit_refund_qualified_property_taxes", period
        )
        taxes_available = tax_unit(
            "mn_homestead_credit_refund_property_taxes_available", period
        )
        claimants = tax_unit.members("is_tax_unit_head_or_spouse", period)
        claimant_is_tax_unit_dependent = tax_unit.any(
            claimants & tax_unit.members("is_tax_unit_dependent", period)
        )
        claimant_is_dependent_elsewhere = tax_unit(
            "head_is_dependent_elsewhere", period
        ) | tax_unit("spouse_is_dependent_elsewhere", period)
        claimant_is_dependent = (
            claimant_is_tax_unit_dependent | claimant_is_dependent_elsewhere
        )
        return (
            taxes_available
            & (property_tax > 0)
            & ~claimant_is_dependent
            & (p.max_refund.calc(household_income) > 0)
        )
