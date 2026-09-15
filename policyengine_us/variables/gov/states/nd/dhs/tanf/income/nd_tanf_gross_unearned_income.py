from policyengine_us.model_api import *


class nd_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "North Dakota TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_55_20_15.htm"
    defined_for = StateCode.ND

    adds = "gov.states.nd.dhs.tanf.income.sources.unearned"
