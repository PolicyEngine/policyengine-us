from policyengine_us.model_api import *


class sc_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF resources eligible"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://www.law.cornell.edu/regulations/south-carolina/S.C.-Code-Regs.-114-1140"  # Section (C)

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.resources
        # Inputs are stored as float32, so compare whole cents with the limit.
        assets = round_to_cents(spm_unit("sc_tanf_countable_resources", period))
        return assets <= p.limit
