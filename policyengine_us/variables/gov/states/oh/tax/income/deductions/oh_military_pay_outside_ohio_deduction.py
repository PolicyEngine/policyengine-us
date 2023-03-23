from policyengine_us.model_api import *


class oh_military_pay_outside_ohio_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OH military received by Ohio residents while stationed outside Ohio deduction"
    definition_period = YEAR
    unit = USD
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=4"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        person_deduction = person("military_service_income", period) #? 
        return tax_unit.sum(person_deduction)
