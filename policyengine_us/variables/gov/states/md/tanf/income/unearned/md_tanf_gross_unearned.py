from policyengine_us.model_api import *


class md_tanf_gross_unearned(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    adds = "gov.states.md.tanf.income.sources.unearned"
