from policyengine_us.model_api import *


class medicaid_magi_person(Variable):
    value_type = float
    entity = Person
    label = "Person-level Medicaid MAGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#e_14_G",
        "https://www.law.cornell.edu/uscode/text/26/36B#d_2",
    )

    def formula(person, period, parameters):
        agi = person("medicaid_adjusted_gross_income_person", period)
        additions = parameters(period).gov.hhs.medicaid.income.modification
        person_level_additions = [
            addition
            for addition in additions
            if addition == "tax_exempt_interest_income"
        ]
        tax_unit_level_additions = [
            addition for addition in additions if addition not in person_level_additions
        ]
        filing_status = person.tax_unit("filing_status", period)
        frac = where(
            filing_status == filing_status.possible_values.JOINT,
            0.5,
            1.0,
        )
        shared_additions = (
            person("is_tax_unit_head_or_spouse", period)
            * add(person.tax_unit, period, tax_unit_level_additions)
            * frac
        )
        return max_(
            0,
            agi + add(person, period, person_level_additions) + shared_additions,
        )
