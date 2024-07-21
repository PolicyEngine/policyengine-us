from policyengine_us.model_api import *


class is_early_head_start_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Early Head Start program"
    definition_period = YEAR
    reference = (
        "https://eclkc.ohs.acf.hhs.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibility"
        "https://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html"
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        p = parameters(period).gov.hhs.head_start

        programs = add(tax_unit, period, p.categorical_eligibility)
        is_program_eligible = np.any(programs)

        federal_agi = tax_unit("adjusted_gross_income", period)
        is_income_eligible = federal_agi <= tax_unit("tax_unit_fpg", period)

        age = person("age", period)
        is_age_eligible = (age < p.early_head_start.age_limit) | person(
            "is_pregnant", period
        )

        return is_age_eligible & (is_income_eligible | is_program_eligible)
