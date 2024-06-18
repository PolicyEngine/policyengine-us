from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_household_resource_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Michigan homestead property tax credit household resource exemption"
    )
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

        # Line 33
        total_household_resources = tax_unit("mi_household_resources", period)
        # Line 5
        # disabled
        disabled_head_or_spouse = tax_unit(
            "disabled_tax_unit_head_or_spouse", period
        )
        # seniors
        senior_eligible = tax_unit("mi_is_senior_for_tax", period)
        # Line 34
        disabled_or_senior_exemption_rate = p.exemption.senior_disabled.calc(
            total_household_resources, right=True
        )
        exemption_rate = where(
            disabled_head_or_spouse | senior_eligible,
            disabled_or_senior_exemption_rate,
            p.exemption.non_senior_disabled,
        )
        exemption_amount = max_(total_household_resources * exemption_rate, 0)
        # Line 13
        property_and_rent = tax_unit(
            "mi_homestead_property_tax_credit_countable_property_tax", period
        )
        # Line 35
        return max_(property_and_rent - exemption_amount, 0)
