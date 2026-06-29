from policyengine_us.model_api import *


class ks_tanf_is_assistance_unit_member(Variable):
    value_type = bool
    entity = Person
    label = "Kansas TANF assistance unit member"
    definition_period = YEAR
    default_value = True
    defined_for = StateCode.KS
    reference = "https://content.dcf.ks.gov/ees/keesm/current/keesm4113.htm"

    def formula(person, period, parameters):
        # Per KEESM 4113: SSI recipients are excluded from the TAF assistance
        # unit, so they are left out of its size, income, and benefit.
        return person("applicable_ssi", period) == 0
