from policyengine_us.model_api import *


class mt_tanf_gross_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "Montana Temporary Assistance for Needy Families (TANF) gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MT

    adds = "gov.states.mt.dhs.tanf.income.sources.earned"
