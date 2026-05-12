from policyengine_us.model_api import *


class ar_medicaid_work_requirement_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible under the Arkansas historical Medicaid work requirement approximation"
    )
    definition_period = YEAR
    reference = (
        "https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/81021",
        "https://www.kff.org/medicaid/issue-brief/state-data-for-medicaid-work-requirements-in-arkansas/",
        "https://www.law.cornell.edu/regulations/arkansas/016-20-18-Ark-Code-R-003",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.dhs.medicaid.work_requirements
        subject = person("ar_medicaid_work_requirement_subject", period)

        # Arkansas' waiver operated with monthly reporting and three-month lockout
        # rules, but the default microdata are annual. This approximation only uses
        # the parts of the waiver that are observable in yearly data. Reporting
        # compliance, good-cause months, treatment-program participation, and
        # other administrative exemptions are therefore left out.
        monthly_hours_worked = person("monthly_hours_worked", period)
        meets_monthly_work_hours = monthly_hours_worked >= p.monthly_hours_threshold

        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_pregnant = person("is_pregnant", period)
        is_full_time_student = person("is_full_time_student", period)
        is_disabled = person("is_disabled", period)
        is_blind = person("is_blind", period)
        is_incapable_of_self_care = person("is_incapable_of_self_care", period)

        has_eligible_dependent_child = person.tax_unit.any(
            is_dependent & (age <= p.dependent_age_limit)
        )
        has_disabled_dependent = person.tax_unit.any(
            is_dependent & (is_disabled | is_blind | is_incapable_of_self_care)
        )
        receives_unemployment_compensation = (
            person("unemployment_compensation", period) > 0
        )
        eligible_disabled = is_disabled | is_blind | is_incapable_of_self_care

        observable_exemption = (
            is_pregnant
            | is_full_time_student
            | eligible_disabled
            | has_eligible_dependent_child
            | has_disabled_dependent
            | receives_unemployment_compensation
        )

        return ~subject | observable_exemption | meets_monthly_work_hours
