from policyengine_us.model_api import *


class dc_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF need standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.dc.dhs.tanf.need_standard
        base = p.main[unit_size]
        # Add childcare addition, which depends on the child's age.
        person = spm_unit.members
        child = person("is_child", period)
        age = person("monthly_age", period)
        has_childcare_expenses = add(spm_unit, period, ["pre_subsidy_childcare_expenses"]) > 0
        # Look up supplement by age, and limit to children.
        person_childcare_supplement = p.additional_childcare.calc(age) * child
        # Aggregate person-level childcare supplement to SPM unit.
        spm_unit_childcare_supplement = has_childcare_expenses * spm_unit.sum(
            person_childcare_supplement
        )
        return base + spm_unit_childcare_supplement
