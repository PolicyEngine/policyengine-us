from policyengine_us.model_api import *


class is_head_start_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Early Head Start or Head Start income eligible"
    definition_period = YEAR
    reference = (
        "https://eclkc.ohs.acf.hhs.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibility"
        "https://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html"
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        federal_agi = tax_unit("adjusted_gross_income", period)
        return federal_agi <= tax_unit("tax_unit_fpg", period)
