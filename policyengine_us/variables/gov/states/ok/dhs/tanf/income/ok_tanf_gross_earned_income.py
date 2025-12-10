from policyengine_us.model_api import *


class ok_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-31"
    )
    defined_for = StateCode.OK

    adds = "gov.states.ok.dhs.tanf.income.sources.earned"
