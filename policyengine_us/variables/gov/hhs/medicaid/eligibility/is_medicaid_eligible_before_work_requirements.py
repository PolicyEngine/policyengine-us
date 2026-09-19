from policyengine_us.model_api import *


class is_medicaid_eligible_before_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Medicaid before any work requirement"
    definition_period = YEAR
    documentation = (
        "Medicaid eligibility from the categorical and immigration tests (or a "
        "state-funded program), before the federal community engagement "
        "requirement and any state work requirement. The community engagement "
        "requirement applies only to the adult expansion group and its "
        "section 1115 equivalents (42 U.S.C. 1396a(xx)(9)(A)), and it exempts "
        "people who are blind or disabled and excludes people aged 65 or "
        "over, so this equals is_medicaid_eligible for SSI recipients and "
        "other aged, blind or disabled people. Programs that condition a "
        "payment on such a person's Medicaid status should read this "
        "variable: the community engagement pass-through reads SNAP, SNAP "
        "counts those payments as unearned income, and reading "
        "is_medicaid_eligible from them closes a dependency cycle from 2027 "
        "(issue #9534)."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=236",
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
