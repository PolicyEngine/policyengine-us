from policyengine_us.model_api import *


class food_excise(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii food and excise tax credit"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://www.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0055_0085.htm"

    def formula(tax_unit, period, parameters):
        #what is tax_unit?
        person = tax_unit.members

        single_params = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax.AGI_single
        married_params = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax.AGI_married

        if person.status = single: 
            single_credit = person.income in single_params
            return single_credit*number of qualified persons + number of minor children*110

        if person.status = married:
            married_credit = person.income in married_params
            return married_credit*number of qualified persons + number of minor children*110

        
