from policyengine_us.model_api import *


class mi_allowable_homestead_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan allowable homestead property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-508",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2",
    )
    defined_for = "mi_homestead_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax

        total_household_resources = tax_unit("mi_household_resources", period)
        exemption_amount = tax_unit(
            "mi_homestead_property_tax_credit_household_resource_exemption",
            period,
        )
        # seniors
        # SECTION A: SENIOR CLAIMANTS (if you checked only box 5a)
        senior_eligible = tax_unit("mi_is_senior_for_tax", period)
        # Line 37
        # The reduction is specified as going from 100% to 0% rather than vice-versa.
        phase_out_rate = p.rate.senior.base.calc(
            total_household_resources, right=True
        )
        # Line 38
        uncapped_senior_amount = phase_out_rate * exemption_amount
        senior_amount = min_(uncapped_senior_amount, p.cap)

        # disabled or (disabled & seniors)
        # SECTION B: DISABLED CLAIMANTS (if you checked only box 5b, or both boxes 5a and 5b)
        # Line 5
        disabled_head_or_spouse = tax_unit(
            "disabled_tax_unit_head_or_spouse", period
        )
        # Line 39
        head_and_spouse_disabled_amount = min_(exemption_amount, p.cap)

        # others
        # SECTION C: ALL OTHER CLAIMANTS (if you did not check box 5a or 5b)
        # Line 41
        uncapped_credit_amount = p.rate.non_senior_disabled * exemption_amount
        other_amount = min_(uncapped_credit_amount, p.cap)
        # Line 42
        return select(
            [disabled_head_or_spouse, senior_eligible],
            [head_and_spouse_disabled_amount, senior_amount],
            default=other_amount,
        )
