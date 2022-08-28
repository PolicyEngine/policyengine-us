from openfisca_us.model_api import *


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
        any_housing_cost = tax_unit.household("pays_property_tax_or_rent", period)
        
        
        #calculate credit amount
        credit = tax_unit("mo_property_tax_credit_amount", period)
        
        return demographic_qualification * any_housing_cost * credit
