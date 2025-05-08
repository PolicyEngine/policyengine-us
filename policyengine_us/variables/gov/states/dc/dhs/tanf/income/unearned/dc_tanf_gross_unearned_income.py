from policyengine_us.model_api import *


class dc_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "DC Temporary Assistance for Needy Families (TANF) gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC

    adds = "gov.states.dc.dhs.tanf.income.sources.unearned"
