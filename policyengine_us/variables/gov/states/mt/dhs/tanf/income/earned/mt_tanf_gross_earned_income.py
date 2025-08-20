from policyengine_us.model_api import *


class mt_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Montana Temporary Assistance for Needy Families (TANF) gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MT

    # adds employment_income and self_employment_income
    # do these cover all sources of countable income?
    adds = "gov.states.mt.dhs.tanf.income.sources.earned"