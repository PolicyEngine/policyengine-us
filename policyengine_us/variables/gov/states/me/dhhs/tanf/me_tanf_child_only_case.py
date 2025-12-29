from policyengine_us.model_api import *


class me_tanf_child_only_case(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maine TANF child-only case"
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # A child-only case is when there is no adult included in the
        # assistance unit. This uses different payment standards.
        person = spm_unit.members
        is_adult = person("is_adult", period)
        return ~spm_unit.any(is_adult)
