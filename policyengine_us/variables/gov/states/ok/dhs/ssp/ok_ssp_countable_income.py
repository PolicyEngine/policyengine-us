from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ok.dhs.ssp._ok_ssp_income import ok_ssp_income


class ok_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma SSP countable income"
    definition_period = MONTH
    unit = USD
    reference = "https://www.oklahoma.gov/ohca/policies-and-rules/xpolicy/medical-assistance-for-adults-and-children-eligibility/eligibility-and-countable-income/countable-income-and-resources/determination-of-countable-income-for-individuals-categorically-.html"

    def formula(person, period, parameters):
        return ok_ssp_income(person, period, parameters, combined=True)
