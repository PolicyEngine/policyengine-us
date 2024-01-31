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
        ).gov.states.mi.tax.income.credits.homestead_property_tax
        p2 = parameters(period).gov.states.mi.tax.income
        # Line 33
        total_household_resources = tax_unit("mi_household_resources", period)
        # Line 5
        # disabled
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disabled_people = person("is_disabled", period)
        disabled_eligible = (
            tax_unit.sum(disabled_people & is_head_or_spouse) > 0
        )
        # seniors
        age_older = tax_unit("greater_age_head_spouse", period)
        senior_eligible = age_older >= p2.senior_age
        # Line 34
        disabled_or_senior_non_refundable_rate = (
            p.exemption.senior_disabled.calc(total_household_resources)
        )
        non_refundable_rate = where(
            disabled_eligible | senior_eligible,
            disabled_or_senior_non_refundable_rate,
            p.exemption.non_senior_disabled,
        )
        non_refundable_amount = max_(
            total_household_resources * non_refundable_rate, 0
        )
        # Line 13
        property_and_rent = tax_unit(
            "mi_homestead_property_tax_credit_property_and_rent_value", period
        )
        # Line 35
        return max_(property_and_rent - non_refundable_amount, 0)
