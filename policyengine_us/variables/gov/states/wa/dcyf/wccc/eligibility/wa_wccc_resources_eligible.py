from policyengine_us.model_api import *


class wa_wccc_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Resource eligible for Washington WCCC"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005"

    def formula(spm_unit, period, parameters):
        assets = spm_unit("spm_unit_assets", period.this_year)
        limit = parameters(period).gov.states.wa.dcyf.wccc.eligibility.resources.limit
        return assets <= limit
