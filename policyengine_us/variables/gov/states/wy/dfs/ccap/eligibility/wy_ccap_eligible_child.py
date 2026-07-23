from policyengine_us.model_api import *


class wy_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Wyoming Child Care, Purchase of Service"
    definition_period = MONTH
    defined_for = StateCode.WY
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1 §8(e)(i)(A), (e)(ii), eff. 05/07/2025 (PDF pp. 16, 18)
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",  # Wyoming DFS Child Care Subsidy Policy Manual §601 (PDF p. 1)
    )

    def formula(person, period, parameters):
        # Rules Ch. 1 §8(e)(i)(A): a child must be under 13, or 13 through
        # under 18 if the child has special needs, is developmentally delayed,
        # or is physically or mentally incapable of self-care, or is under
        # court supervision. We don't track court supervision at the moment,
        # so the extension applies only via the special-needs branch.
        p = parameters(period).gov.states.wy.dfs.ccap.eligibility
        age = person("age", period.this_year)
        has_special_need = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        age_limit = where(
            has_special_need, p.special_needs_child_age_limit, p.child_age_limit
        )
        age_eligible = age < age_limit
        # §8(e)(ii): the eligible child must be a U.S. citizen or legally
        # residing alien; Wyoming applies no citizenship or Social Security
        # number test to the applicant or caretaker (§8(e)(ii)(E)).
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
