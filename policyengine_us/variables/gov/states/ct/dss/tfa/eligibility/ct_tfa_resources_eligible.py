from policyengine_us.model_api import *


class ct_tfa_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Connecticut Temporary Family Assistance (TFA) due to resources"
    )
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=10"
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.resource
        # Inputs are stored as float32, so compare whole cents with the limit.
        assets = round_to_cents(spm_unit("spm_unit_cash_assets", period.this_year))
        return assets <= p.limit
