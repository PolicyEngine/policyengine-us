from policyengine_us.model_api import *


class ks_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm4113.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # SSI recipients are excluded from the assistance unit (KEESM 4113), so
        # their unearned income is not counted.
        person = spm_unit.members
        is_member = person("ks_tanf_is_assistance_unit_member", period.this_year)
        unearned = person("tanf_gross_unearned_income", period)
        return spm_unit.sum(unearned * is_member)
