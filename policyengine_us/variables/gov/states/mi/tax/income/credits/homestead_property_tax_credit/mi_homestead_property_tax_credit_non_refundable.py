from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan non-refundable homestead property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-508",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        total_household_resources = tax_unit(
            "mi_household_resources", period
        )  # Line 33

        # disabled
        person = tax_unit.members
        is_head_or_spouse = person(
            "is_tax_unit_head_or_spouse", period
        )  # Line 5
        disabled_people = person("is_disabled", period)  # Line 5
        disabled_eligible = (
            tax_unit.sum(disabled_people & is_head_or_spouse) > 0
        )
        # seniors
        age_older = tax_unit("greater_age_head_spouse", period)  # Line 5
        senior_eligible = age_older >= p.senior.min_age

        non_refundable_rate = where(
            disabled_eligible | senior_eligible,
            p.disabled_or_senior.not_refundable_rate.calc(
                total_household_resources
            ),
            p.rate.not_refundable,
        )
        non_refundable_amount = max_(
            total_household_resources * non_refundable_rate, 0
        )  # Line 34

        property_and_rent = tax_unit(
            "mi_homestead_property_tax_credit_property_and_rent_value", period
        )  # Line 13
        return max_(property_and_rent - non_refundable_amount, 0)  # Line 35
