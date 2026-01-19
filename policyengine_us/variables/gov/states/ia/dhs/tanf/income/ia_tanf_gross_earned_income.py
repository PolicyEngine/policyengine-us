from policyengine_us.model_api import *


class ia_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    adds = "gov.states.ia.dhs.tanf.income.sources.earned"
