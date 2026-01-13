from policyengine_us.model_api import *


class ia_tanf_fip_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP income limit (185% of living costs)"
    unit = USD
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.28"
    documentation = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.tanf.fip

        family_size = spm_unit("ia_tanf_fip_family_size", period)

        # Get base income limit for family size up to 10
        base_size = min_(family_size, 10)
        income_limit = p.income_limit[base_size]

        # Add increment for each additional member beyond 10
        additional_members = max_(family_size - 10, 0)
        additional_amount = additional_members * p.income_limit_additional

        return income_limit + additional_amount
