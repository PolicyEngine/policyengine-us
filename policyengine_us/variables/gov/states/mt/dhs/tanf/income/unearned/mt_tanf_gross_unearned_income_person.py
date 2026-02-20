from policyengine_us.model_api import *


class mt_tanf_gross_unearned_income_person(Variable):
    value_type = float
    entity = Person
    label = "Montana Temporary Assistance for Needy Families (TANF) gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF501-1Jan012018.pdf#page=1"
    defined_for = StateCode.MT

    adds = "gov.states.mt.dhs.tanf.income.sources.unearned"
