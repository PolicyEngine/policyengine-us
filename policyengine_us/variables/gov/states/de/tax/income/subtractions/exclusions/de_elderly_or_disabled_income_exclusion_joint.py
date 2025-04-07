from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware individual aged or disabled exclusion when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-01_PaperInteractive.pdf#page=1"
    defined_for = "de_elderly_or_disabled_income_exclusion_eligible_person"

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.elderly_or_disabled

        # If filing jointly, both spouses have to be eligible.
        joint = filing_status == filing_status.possible_values.JOINT

        head = person("is_tax_unit_head", period)

        spouse = person("is_tax_unit_spouse", period)

        eligible_person = person(
            "de_elderly_or_disabled_income_exclusion_eligible_person", period
        )

        eligible_head_present = tax_unit.any(head & eligible_person)

        eligible_spouse_present = tax_unit.any(spouse & eligible_person)

        eligible_joint_unit = eligible_head_present & eligible_spouse_present

        eligible_unit = where(joint, eligible_joint_unit, eligible_person)
        return p.amount[filing_status] * eligible_unit
