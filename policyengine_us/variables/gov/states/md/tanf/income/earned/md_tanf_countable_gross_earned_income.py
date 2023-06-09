from policyengine_us.model_api import *


class md_tanf_countable_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF countable gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    adds = "gov.states.md.tanf.income.sources.earned"
