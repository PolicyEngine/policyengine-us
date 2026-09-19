from policyengine_us.model_api import *


class is_medicaid_eligible_before_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Medicaid before any work requirement"
    definition_period = YEAR
    documentation = (
        "Medicaid eligibility from the categorical and immigration tests (or a "
        "state-funded program), before the federal community engagement "
        "requirement and any state work requirement. Read this in place of "
        "is_medicaid_eligible only for people the requirement cannot reach. "
        "An applicable individual is one eligible under 42 U.S.C. "
        "1396a(a)(10)(A)(i)(VIII), the under-65 adult group, or an equivalent "
        "section 1115 group (1396a(xx)(9)(A)(i)). Subclause (VIII) excludes "
        "anyone described in an earlier subclause, which covers SSI "
        "recipients, and the blind or disabled are specified excluded "
        "individuals (1396a(xx)(9)(A)(ii)(V)(aa)). For those people this "
        "equals is_medicaid_eligible in every year. State supplements "
        "conditioned on their Medicaid status read this variable because the "
        "community engagement pass-through reads SNAP and SNAP counts those "
        "supplements as unearned income, so reading is_medicaid_eligible "
        "from them closes a dependency cycle from 2027 (issue #9534)."
    )
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396a&num=0&edition=prelim",
        "https://www.law.cornell.edu/cfr/text/42/435.551",
    )

    def formula(person, period, parameters):
        category = person("medicaid_category", period)
        categorically_eligible = category != category.possible_values.NONE
        immigration_status_eligible = person(
            "is_medicaid_immigration_status_eligible", period
        )
        return (
            (categorically_eligible & immigration_status_eligible)
            | person("ca_ffyp_eligible", period)
            | person("il_hbi_eligible", period)
        )
