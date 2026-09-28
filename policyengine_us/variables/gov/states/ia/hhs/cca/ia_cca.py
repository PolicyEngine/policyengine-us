from policyengine_us.model_api import *


class ia_cca(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Iowa CCA benefit amount"
    definition_period = MONTH
    defined_for = "ia_cca_eligible"
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=14"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_in_care = person("ia_cca_eligible_child", period) & (
            person("childcare_hours_per_week", period.this_year) > 0
        )
        # Iowa pays the provider's charge for each child, not to exceed the
        # maximum rate ceiling (rate per half-day unit times the child's
        # monthly units of care), then subtracts the family fee
        # (IAC 441-170.4(7)"a").
        child_charge = person("pre_subsidy_childcare_expenses", period)
        max_rate = person("ia_cca_max_rate", period)
        monthly_units = person("ia_cca_monthly_units", period)
        child_ceiling = max_rate * monthly_units
        child_capped = min_(child_charge, child_ceiling)
        total_capped = spm_unit.sum(child_capped * is_in_care)
        copay = spm_unit("ia_cca_copay", period)
        return max_(total_capped - copay, 0)
