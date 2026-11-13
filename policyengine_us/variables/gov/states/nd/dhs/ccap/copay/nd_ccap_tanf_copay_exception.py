from policyengine_us.model_api import *


class nd_ccap_tanf_copay_exception(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "North Dakota CCAP family has an exception to the TANF or Diversion co-payment waiver"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_45_05.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/Archive%20Documents/2011%20-%203278%2C%203295%2C%203327/400_28_90_20%20ML3295.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/Archive%20Documents/2023/ML%203732/400_28_90_20.htm",
        # PDF pages 3-4
        "https://www.nd.gov/dhs/policymanuals/40028/Content/ML/2026/CCAP%20Release%2026.3%20Effective%20October.1.2026.pdf#page=3",
    )

    def formula_2011_10_01(spm_unit, period, parameters):
        # Until October 2026, North Dakota charged the co-pay when child care
        # resulted from the activity of a TANF caretaker who received SSI
        # (400-28-90-20 and the repealed 400-28-45-15).
        person = spm_unit.members
        caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        caretaker_ssi = spm_unit.any(caretaker & (person("ssi", period) > 0))
        alien = spm_unit("nd_ccap_has_disqualified_alien_caretaker", period)
        non_legally_responsible = spm_unit(
            "nd_ccap_has_ineligible_non_legally_responsible_caretaker", period
        )
        return caretaker_ssi | alien | non_legally_responsible

    def formula_2021_04_01(spm_unit, period, parameters):
        person = spm_unit.members
        caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        caretaker_ssi = spm_unit.any(caretaker & (person("ssi", period) > 0))
        alien = spm_unit("nd_ccap_has_disqualified_alien_caretaker", period)
        non_legally_responsible = spm_unit(
            "nd_ccap_has_ineligible_non_legally_responsible_caretaker", period
        )
        kinship = spm_unit("nd_ccap_has_ineligible_kinship_caretaker", period)
        return caretaker_ssi | alien | non_legally_responsible | kinship

    def formula_2026_10_01(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.nd.dhs.ccap.eligibility
        # Include children under 18 and North Dakota's older disabled children,
        # without imposing the separate CCAP immigration test on SSI receipt.
        child = person("is_child", period.this_year) | (
            person("is_disabled", period.this_year)
            & (person("age", period.this_year) < p.disabled_child_age_limit)
        )
        # North Dakota charges the co-pay for "child care for an SSI child"
        # (400-28-45-05), so the waiver holds when the SSI child attends no
        # care. When an SSI child attends care, the model charges the whole
        # family co-payment, including for a sibling whose care stays waived.
        in_care = person("nd_ccap_child_in_care", period)
        child_receives_ssi = spm_unit.any(child & in_care & (person("ssi", period) > 0))
        alien = spm_unit("nd_ccap_has_disqualified_alien_caretaker", period)
        non_legally_responsible = spm_unit(
            "nd_ccap_has_ineligible_non_legally_responsible_caretaker", period
        )
        kinship = spm_unit("nd_ccap_has_ineligible_kinship_caretaker", period)
        tanf_child = spm_unit("nd_ccap_has_tanf_eligible_child", period)
        return (
            child_receives_ssi
            | alien
            | non_legally_responsible
            | (kinship & ~tanf_child)
        )
