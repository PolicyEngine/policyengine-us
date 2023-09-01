from policyengine_us.model_api import *


class ca_tanf_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    adds = "gov.states.ca.cdss.tanf.income.sources.earned"