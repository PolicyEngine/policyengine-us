from policyengine_us.model_api import *


class mo_tanf_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF income limit / maximum benefit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        assistance_unit_size = spm_unit("mo_tanf_assistance_unit_size", period)
        p = parameters(period).gov.states.mo.dss.tanf

        # For income limit purposes, use the standard of need
        # Capped at max_table_size (8 persons) per regulations
        max_size = p.income_limit.max_table_size
        capped_size = min_(assistance_unit_size, max_size).astype(int)

        # Get the standard of need for the capped size
        # This is used for the 185% gross income test
        return p.standard_of_need.amount[capped_size]
