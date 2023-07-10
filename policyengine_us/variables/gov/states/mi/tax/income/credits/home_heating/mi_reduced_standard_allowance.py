## line_40 of tax form
from policyengine_us.model_api import *


class mi_reduced_standard_allowance(Variable):
    value_type = float
    entity = TaxUnit
    label = "mi_reduced_standard_allowance"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
       
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit.total_household_resources

        mi_household_resources = tax_unit("mi_household_resources",period)
        standard_allowance=tax_unit("mi_standard_allowance",period)
       

        # determine mi_reduced_standard_allowance
        return max((standard_allowance - p.total_household_resources_rate * mi_household_resources),0)
       

 