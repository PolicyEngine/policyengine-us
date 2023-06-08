from policyengine_us.model_api import *


class nh_person_base_exemption(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire person level base exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(person, period, parameters):

        individual_income = person("dividend_income", period) + person("interest_income", period) 
        p = parameters(period).gov.states.nh.tax.income.exemptions.amount
        
        return where(individual_income < p.base, individual_income, p.base)
        

