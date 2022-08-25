from openfisca_us.model_api import *
from openfisca_us.variables.gov.states.mo.tax.income.credits.mo_property_tax_credit_housing_payment_test import mo_property_tax_credit_housing_payment_test
from openfisca_us.variables.gov.states.mo.tax.income.credits.mo_property_tax_credit_rent_or_own import mo_property_tax_credit_rent_or_own

class mo_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        ##Demographic Eligibility
        demographic_qualification = tax_unit("mo_property_tax_credit_demographic_tests", period)
        
        #rent or property_tax test
        any_housing_cost = tax_unit("mo_property_tax_credit_housing_payment_test", period)
        housing_and_demographic_test = (any_housing_cost + demographic_qualification) == 2
        
        #calculate credit amount
        credit = tax_unit("mo_property_tax_credit_amount", period)
        
        return where(housing_and_demographic_test == 1, credit, 0)
        
 
        
        

        