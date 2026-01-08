from policyengine_us.model_api import *


class va_up_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF-UP eligibility"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/700_07-20.pdf#page=2"
    documentation = """
    Virginia TANF-UP (Unemployed Parent) Program eligibility requires:
    - Two able-bodied natural or adoptive parents in the home
    - At least one child in common
    - Neither parent meets disability exemption criteria (Section 901.2 C. or D.)

    Per VA TANF Manual 701.1: "The TANF-UP Program is intended to provide
    assistance to families with two able-bodied parents."

    Per VA TANF Manual 701.3: "The standard filing unit is required to include
    two able-bodied natural or adoptive parents."
    """

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        disabled = person("is_disabled", period)
        able_bodied_adult = head_or_spouse & ~disabled
        return spm_unit.sum(able_bodied_adult) >= 2
