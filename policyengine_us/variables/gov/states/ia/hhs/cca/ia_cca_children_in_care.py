from policyengine_us.model_api import *


class ia_cca_children_in_care(Variable):
    value_type = int
    entity = SPMUnit
    label = "Iowa CCA number of children in care"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=15"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_eligible_child = person("ia_cca_eligible_child", period)
        # A child is in care if they have childcare hours scheduled.
        # `childcare_hours_per_week` is YEAR-defined.
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        return spm_unit.sum(is_eligible_child & in_care)
