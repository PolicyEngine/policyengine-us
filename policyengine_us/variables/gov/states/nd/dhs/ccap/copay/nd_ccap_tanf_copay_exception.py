from policyengine_us.model_api import *


class nd_ccap_tanf_copay_exception(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "North Dakota CCAP family has an exception to the TANF or Diversion co-payment waiver"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_45_05.htm",
    )

    def formula_2011_10_01(spm_unit, period, parameters):
        alien = spm_unit("nd_ccap_has_disqualified_alien_caretaker", period)
        non_legally_responsible = spm_unit(
            "nd_ccap_has_ineligible_non_legally_responsible_caretaker", period
        )
        return alien | non_legally_responsible

    def formula_2021_04_01(spm_unit, period, parameters):
        alien = spm_unit("nd_ccap_has_disqualified_alien_caretaker", period)
        non_legally_responsible = spm_unit(
            "nd_ccap_has_ineligible_non_legally_responsible_caretaker", period
        )
        kinship = spm_unit("nd_ccap_has_ineligible_kinship_caretaker", period)
        return alien | non_legally_responsible | kinship

    def formula_2026_10_01(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.nd.dhs.ccap.eligibility
        # Include children under 18 and North Dakota's older disabled children,
        # without imposing the separate CCAP immigration test on SSI receipt.
        child = person("is_child", period.this_year) | (
            person("is_disabled", period.this_year)
            & (person("age", period.this_year) < p.disabled_child_age_limit)
        )
        child_receives_ssi = spm_unit.any(child & (person("ssi", period) > 0))
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
