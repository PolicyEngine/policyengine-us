from policyengine_us.model_api import *


class mo_tanf_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF income limit / maximum benefit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.mo.dss.tanf
        # TODO: Find the amount for households with more than 8 people.
        capped_people = min_(people, 8).astype(int)
        # Note: Missouri defines income limits annually.
        return p.income_limit[capped_people]
