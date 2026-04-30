from policyengine_us.model_api import *


class wa_wccc_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Categorically eligible for Washington WCCC"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0023"

    def formula(spm_unit, period, parameters):
        # We don't track CPS/CWS or specialty-court pathways at the moment;
        # only the Homeless Grace Period pathway is modeled.
        return spm_unit.household("is_homeless", period.this_year)
