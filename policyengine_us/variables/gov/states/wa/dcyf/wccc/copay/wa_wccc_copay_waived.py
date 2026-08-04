from policyengine_us.model_api import *


class wa_wccc_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington WCCC copayment is waived"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0075",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0024",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        age = person("age", period.this_year)
        # WAC 110-15-0075(5)(a) waives the copay for parents age 21 or younger
        # attending high school. The HSE-certificate path is not modeled at
        # the moment.
        p = parameters(period).gov.states.wa.dcyf.wccc.copay
        is_teen_parent = (
            is_head_or_spouse & is_in_school & (age <= p.teen_parent_age_limit)
        )
        any_teen_parent = spm_unit.sum(is_teen_parent) > 0
        # WAC 110-15-0075(5)(c)(i) waives the copay for HGP families.
        # WAC 110-15-0075(5)(c)(ii) also waives it for WAC 110-15-0024
        # categorical families (CPS/CWS/specialty courts), which we don't
        # track at the moment.
        # WAC 110-15-0075(5)(b) waives it for ECE-workforce employees, which
        # we don't track at the moment.
        is_hgp_eligible = spm_unit("wa_wccc_hgp_eligible", period)
        return any_teen_parent | is_hgp_eligible
