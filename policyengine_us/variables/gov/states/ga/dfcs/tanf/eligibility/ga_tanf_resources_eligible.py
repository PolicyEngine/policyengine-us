from policyengine_us.model_api import *


class ga_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia TANF due to resources"
    definition_period = MONTH
    reference = (
        "https://rules.sos.ga.gov/gac/290-2-28-.13",
        "https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.resources
        # For simplified implementation, use SPM unit cash assets directly
        # In a more complete implementation, this would account for
        # excluded resources (primary residence, household goods, etc.)
        # and vehicle value limits
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)
        return cash_assets <= p.limit
