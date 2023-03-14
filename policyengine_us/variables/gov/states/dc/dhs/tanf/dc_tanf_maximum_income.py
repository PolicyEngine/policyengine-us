from policyengine_us.model_api import *


class dc_tanf_maximum_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF maximum income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.eligibility.maximum_income
        base = p.main[unit_size]
        # Add childcare addition, which depends on the child's age.
        person = spm_unit.members
        child = person("is_child", period)
        age = person("age", period)
        has_childcare_expenses = spm_unit("childcare_expenses", period) > 0
        # Look up supplement by age, and limit to children.
        person_childcare_supplement = p.childcare.calc(age) * child
        # Aggregate person-level childcare supplement to SPM unit.
        spm_unit_childcare_supplement = has_childcare_expenses * spm_unit.sum(
            person_childcare_supplement
        )
        monthly_maximum = base + spm_unit_childcare_supplement
        return monthly_maximum * MONTHS_IN_YEAR
