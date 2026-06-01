from policyengine_us.model_api import *


class wa_wccc_hgp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington WCCC Homeless Grace Period eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = ("https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0023",)
    # WAC 110-15-0023 establishes the Homeless Grace Period (HGP), which
    # bypasses the asset limit and income tier. WAC 110-15-0024 categorical
    # eligibility (CPS/CWS/specialty courts) is not modeled at the moment.

    def formula(spm_unit, period, parameters):
        return spm_unit.household("is_homeless", period.this_year)
