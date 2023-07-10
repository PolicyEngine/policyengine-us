from policyengine_us.model_api import *


class heating_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Household heating cost credit"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
    )
    
    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit

        rent_include_heating_cost=tax_unit("rent_include_heating_cost",period)
        mi_reduced_standard_allowance=tax_unit("mi_reduced_standard_allowance",period)
        mi_alternate_household_credit=tax_unit("mi_alternate_household_credit",period)
        standard_allowance=tax_unit("mi_standard_allowance",period)
        mi_household_resources=tax_unit("mi_household_resources",period)
        heating_cost=tax_unit("heating_cost",period)

        # calculate initial home heating credit
        ini_hhc=where(
            rent_include_heating_cost==True,
            (p.standard_allowance.reduced_standard_allowance_rate * mi_reduced_standard_allowance),
            max(mi_reduced_standard_allowance,mi_alternate_household_credit)
            )

        # determine final home heating credit
        return p.home_heating_credit_rate * ini_hhc
       



       
