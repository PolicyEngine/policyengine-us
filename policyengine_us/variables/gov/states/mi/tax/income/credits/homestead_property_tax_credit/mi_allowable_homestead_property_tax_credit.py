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
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        total_household_resources = tax_unit("mi_household_resources", period)
        excess_amount = tax_unit(
            "mi_homestead_property_tax_credit_non_refundable", period
        )

        # seniors
        # SECTION A: SENIOR CLAIMANTS (if you checked only box 5a)
        older_spouse_age_eligible = (
            tax_unit("greater_age_head_spouse", period) >= p.senior.min_age
        )
        phase_out_rate = p.senior.phase_out_rate.calc(
            total_household_resources
        )  # Line 37
        senior_amount = min_(phase_out_rate * excess_amount, p.cap)  # Line 38

        # disabled or (disabled & seniors)
        # SECTION B: DISABLED CLAIMANTS (if you checked only box 5b, or both boxes 5a and 5b)
        person = tax_unit.members
        is_head_or_spouse = person(
            "is_tax_unit_head_or_spouse", period
        )  # Line 5
        is_disabled = person("is_disabled", period)  # Line 5
        disabled_head_or_spouse = (
            tax_unit.sum(is_disabled & is_head_or_spouse) > 0
        )
        head_and_spouse_eligible = (
            older_spouse_age_eligible & disabled_head_or_spouse
        )
        head_and_spouse_disabled_amount = min_(
            excess_amount,
            p.cap,
        )  # Line 39

        # others
        # SECTION C: ALL OTHER CLAIMANTS (if you did not check box 5a or 5b)
        other_amount = min_(
            p.rate.credit * excess_amount,
            p.cap,
        )  # Line 41

        return select(
            [
                (disabled_head_or_spouse | head_and_spouse_eligible),
                older_spouse_age_eligible,
            ],
            [head_and_spouse_disabled_amount, senior_amount],
            default=other_amount,
        )  # Line 42
