from policyengine_us.model_api import *


class mi_standard_home_heating_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard home heating credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
    )
    defined_for = "mi_standard_home_heating_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.credits.home_heating
        # determine count of exemption
        exemption_count = tax_unit("mi_exemptions_count", period)
        # Line 38
        base_amount = p.standard.base.calc(exemption_count)
        # Calculate the additional exemption amount
        additional_exemptions = max_(
            exemption_count - p.additional_exemption.limit, 0
        )
        additional_amount = (
            additional_exemptions * p.additional_exemption.amount
        )
        increased_base = base_amount + additional_amount
        # Line 39
        household_resources = tax_unit("mi_household_resources", period)
        reduced_household_resources = (
            household_resources * p.standard.reduction_rate
        )
        # Line 40
        reduced_base = max_(increased_base - reduced_household_resources, 0)
        # Line 41
        utilities_included_in_rent = tax_unit(
            "utilities_included_in_rent", period
        )
        return where(
            utilities_included_in_rent,
            reduced_base * p.standard.included_heating_cost_rate,
            reduced_base,
        )
