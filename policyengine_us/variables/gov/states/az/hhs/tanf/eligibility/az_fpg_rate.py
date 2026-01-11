from policyengine_us.model_api import *


class az_fpg_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Needy family Federal Poverty Guideline Percentage Limit"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # Determine whether the head-of-household is a non-parent relative
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.rate
        person = spm_unit.members
        tax_unit_head = person("is_tax_unit_head", period)
        parent = person("is_parent_of_filer_or_spouse", period)
        eligible_parent_present = spm_unit.any(tax_unit_head & parent)
        return where(eligible_parent_present, p.base, p.non_parent)
