from policyengine_us.model_api import *


class dc_ccsp_income_test_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income test exemption under DC Child Care Subsidy Program (CCSP)"
    definition_period = MONTH
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=11"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.age_threshold
        person = spm_unit.members
        age = person("monthly_age", period)
        is_disabled = person("is_disabled", period)
        # parent is disabled # income waived
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_disabled_parent = spm_unit.any(is_head_or_spouse & is_disabled)
        # child is homeless # income waived
        is_homeless = spm_unit.household("is_homeless", period)
        # parent is teen parent (age <= 19) # income waived
        is_teen_parent = age <= p.teen_parent
        has_teen_parent = spm_unit.any(is_head_or_spouse & is_teen_parent)
        # Manual 2.4.2.1: a qualifying child's court or CFSA protective
        # supervision waives income, activity, and copayment requirements.
        eligible_child = person("dc_ccsp_eligible_child", period)
        court_supervision = person("is_under_court_supervision", period.this_year)
        protective = person("receives_or_needs_protective_services", period.this_year)
        foster = person("is_in_foster_care", period.this_year)
        has_protective_child = spm_unit.any(
            eligible_child & (court_supervision | protective | foster)
        )
        return (
            has_disabled_parent | is_homeless | has_teen_parent | has_protective_child
        )
