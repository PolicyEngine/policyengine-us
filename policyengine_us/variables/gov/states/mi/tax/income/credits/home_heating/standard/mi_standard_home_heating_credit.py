from policyengine_us.model_api import *


class mi_standard_home_heating_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard home heating credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance",
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-527a",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR-7-Book.pdf#page=10",
    )
    defined_for = "mi_standard_home_heating_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.credits.home_heating
        # determine count of exemption
        exemption_count = tax_unit("mi_exemptions_count", period)
        # Line 36: Table A standard allowance for the exemptions claimed.
        base_amount = p.standard.base.calc(exemption_count)
        # Calculate the additional exemption amount
        additional_exemptions = max_(exemption_count - p.additional_exemption.limit, 0)
        additional_amount = additional_exemptions * p.additional_exemption.amount
        increased_base = base_amount + additional_amount
        # Line 37
        household_resources = tax_unit("mi_household_resources", period)
        reduced_household_resources = household_resources * p.standard.reduction_rate
        # Line 38
        reduced_base = max_(increased_base - reduced_household_resources, 0)
        # Line 39: heating costs included in rent halve the standard credit.
        heat_in_rent = tax_unit("mi_home_heating_credit_heat_included_in_rent", period)
        return where(
            heat_in_rent,
            reduced_base * p.standard.included_heating_cost_rate,
            reduced_base,
        )
