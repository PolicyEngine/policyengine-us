from policyengine_us.model_api import *


class ia_cca_income_exception(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa CCA eligible without regard to income"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=4"

    def formula(spm_unit, period, parameters):
        # Iowa serves certain families without regard to income
        # (IAC 441-170.2(1)"b"): FIP/TANF recipients, families with a child
        # in protective child care, and licensed foster parents needing
        # care for a foster child. We use is_tanf_enrolled (a bare input)
        # for the FIP path to break the CCAP-to-TANF circular dependency.
        # PROMISE JOBS remains represented by the existing FIP proxy.
        on_fip = spm_unit("is_tanf_enrolled", period)
        person = spm_unit.members
        protective = person("receives_or_needs_protective_services", period)
        foster = person("is_in_foster_care", period)
        has_protective_or_foster = spm_unit.any(protective | foster)
        ordered_care = person("requires_childcare_under_court_order", period.this_year)
        approved = person("ia_cca_court_ordered_care_approved", period)
        eligible_child = person("ia_cca_eligible_child", period)
        court_exception = spm_unit.any(ordered_care & approved & eligible_child)
        return on_fip | has_protective_or_foster | court_exception
