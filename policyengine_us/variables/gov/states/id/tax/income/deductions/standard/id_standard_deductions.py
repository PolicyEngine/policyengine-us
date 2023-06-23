from policyengine_us.model_api import *


class id_standard_deduction(Variable):
    value_type = float
    #entity = TaxUnit
    entity = Person
    label = "Idaho standard deduction"
    unit = USD
    documentation = "https://tax.idaho.gov/wp-content/uploads/forms/EIS00407/EIS00407_01-05-2023.pdf"
    definition_period = YEAR
    defined_for = StateCode.ID
    
    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.tax.income.deductions.standard
        filing_status = person.tax_unit("filing_status", period)
        base_amt = p.amount[filing_status]

        aged_blind_count = person.tax_unit("aged_blind_count", period)
        extra_amt = aged_blind_count * p.additions[filing_status]

        is_dependent = person("is_tax_unit_dependent", period)



    '''
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        base_amount = p.amount[filing_status]

        is_tax_unit_dependent = person("is_tax_unit_dependent", period)
        return 
    '''