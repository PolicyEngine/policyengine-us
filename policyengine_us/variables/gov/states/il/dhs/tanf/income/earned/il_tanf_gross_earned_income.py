from policyengine_us.model_api import *


class il_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Illinois Temporary Assistance for Needy Families (TANF) gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    adds = "gov.states.il.dhs.tanf.income.sources.earned"
