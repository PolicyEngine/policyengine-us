## line_45 form
from policyengine_us.model_api import *


class mi_alternate_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "mi_alternate_household_credit"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR

    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
    )
    
    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit.standard.allowance

        mi_household_resources = tax_unit("mi_household_resources",period)

        # determine heating cost
        heating_cost=tax_unit("heating_cost",period)

        # determine mi_alternate_household_credit
        return p.alternate_credit_rate * max((min(p.alternate_credit_upperlimit,heating_cost)-mi_household_resources * p.total_household_resources_rate_alternate),0)
       



       
