from policyengine_us.model_api import *


class tx_tanf_work_requirement_exempt(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Exempted from work requirement for Texas Temporary Assistance for Needy Families (TANF)"
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/e-100-participation-texas-works-program",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-1405",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        age = person("monthly_age", period)

        eligible_child = person("tx_tanf_eligible_child", period)

        is_disabled = person("is_ssi_disabled", period)

        is_incapacitated = person(
            "is_permanently_and_totally_disabled", period
        )

        pregnant = person("is_pregnant", period)
        third_trimester = pregnant

        has_young_child = person.spm_unit.any(age < 12)
        lacks_childcare = has_young_child

        return (
            eligible_child
            | is_disabled
            | is_incapacitated
            | third_trimester
            | lacks_childcare
        )
