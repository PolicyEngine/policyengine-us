from policyengine_us.model_api import *


class mi_heating_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household heating cost credit"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit

        heating_costs_included_in_rent = tax_unit(
            "heating_costs_included_in_rent", period
        )
        mi_reduced_standard_allowance = tax_unit(
            "mi_reduced_standard_allowance", period
        )
        mi_alternate_heating_credit = tax_unit(
            "mi_alternate_heating_credit", period
        )
        standard_allowance = tax_unit("mi_standard_allowance", period)
        mi_household_resources = tax_unit("mi_household_resources", period)
        mi_exemption_count = tax_unit("exemptions", period)

        # calculate initial home heating credit
        initial_hhc = where(
            heating_costs_included_in_rent == True,
            mi_reduced_standard_allowance,
            max_(mi_reduced_standard_allowance, mi_alternate_heating_credit),
        )

        return p.home_heating_credit_rate * initial_hhc
