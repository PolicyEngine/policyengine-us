from policyengine_us.model_api import *


class mi_heating_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household heating cost credit"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit

        mi_rent_include_heating_cost = tax_unit(
            "mi_rent_include_heating_cost", period
        )
        mi_reduced_standard_allowance = tax_unit(
            "mi_reduced_standard_allowance", period
        )
        mi_alternate_household_credit = tax_unit(
            "mi_alternate_household_credit", period
        )
        standard_allowance = tax_unit("mi_standard_allowance", period)
        mi_household_resources = tax_unit("mi_household_resources", period)
        mi_exemption_count = tax_unit("mi_exemption_count", period)
        

        # calculate initial home heating credit
        initial_hhc = where(
            mi_rent_include_heating_cost == True,
            (
                p.standard_allowance.reduced_standard_allowance_rate
                * mi_reduced_standard_allowance
            ),
            max_(mi_reduced_standard_allowance, mi_alternate_household_credit)
        )
        # check total house resource comply with alternate credit maximum income  (table B)
        alternate_hhc = where(
            mi_household_resources
            <= p.alternate_credit.maximum_income.calc(mi_exemption_count),
            initial_hhc,
            0,
        )

        # determine final home heating credit
        return p.home_heating_credit_rate * alternate_hhc
