from policyengine_us.model_api import *


class mi_homestead_allowable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan allowable homestead property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-508",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2",
    )
    defined_for = "mi_homestead_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        total_household_resources = tax_unit("mi_household_resources", period)
        exceed_amount = tax_unit(
            "mi_homestead_property_tax_credit_non_refundable", period
        )

        # seniors
        # SECTION A: SENIOR CLAIMANTS (if you checked only box 5a)
        age_older_eligible = (
            tax_unit("greater_age_head_spouse", period) >= p.senior.min_age
        )
        phase_out_rate = p.senior.phase_out_rate.calc(
            total_household_resources
        )  # Line 37
        senior_allowable = min_(
            phase_out_rate * exceed_amount,
            p.max.amount,
        )  # Line 38

        # disabled or disabled & seniors
        # SECTION B: DISABLED CLAIMANTS (if you checked only box 5b, or both boxes 5a and 5b)
        person = tax_unit.members
        is_head_or_spouse = person(
            "is_tax_unit_head_or_spouse", period
        )  # Line 5
        disabled_people = person("is_disabled", period)  # Line 5
        disabled_eligible = (
            tax_unit.sum(disabled_people & is_head_or_spouse) > 0
        )
        both_eligible = age_older_eligible & disabled_eligible
        disabled_both_allowable = min_(
            exceed_amount,
            p.max.amount,
        )  # Line 39

        # others
        # SECTION C: ALL OTHER CLAIMANTS (if you did not check box 5a or 5b)
        credit_rate = p.rate.credit
        other_allowable = min_(
            credit_rate * exceed_amount,
            p.max.amount,
        )  # Line 41

        return select(
            [(disabled_eligible | both_eligible), age_older_eligible],
            [disabled_both_allowable, senior_allowable],
            default=other_allowable,
        )
