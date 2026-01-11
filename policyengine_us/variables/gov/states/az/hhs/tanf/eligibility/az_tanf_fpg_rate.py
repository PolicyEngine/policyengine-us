from policyengine_us.model_api import *


class az_tanf_fpg_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF needy family FPG rate"
    definition_period = YEAR
    reference = "https://dbmefaapolicy.azdes.gov/index.html#page/FAA5/CA_Benefit_Determination.html#wwpID0E0NQB0FA"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Non-parent relatives get 130% FPG; parents get 100% FPG
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.rate

        person = spm_unit.members
        is_head = person("is_tax_unit_head", period)
        is_parent = person("is_parent_of_filer_or_spouse", period)
        has_parent_head = spm_unit.any(is_head & is_parent)

        return where(has_parent_head, p.base, p.non_parent)
