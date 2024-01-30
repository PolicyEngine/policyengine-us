from policyengine_us.model_api import *


class sc_young_child_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina young child deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf#page=2",
        "https://www.scstatehouse.gov/code/t12c006.php",
        # SECTION 12-6-1160
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        # Get relevant parameter subtree.
        p = parameters(period).gov.states.sc.tax.income.deductions.young_child
        # Determine eligibility for each person in the tax unit.
        person = tax_unit.members
        meets_age_limit = person("age", period) < p.ineligible_age
        eligible_dependent = meets_age_limit & person(
            "is_tax_unit_dependent", period
        )
        # Count number of eligible people in the tax unit.
        total_eligible_dependents = tax_unit.sum(eligible_dependent)
        # Multiply by the amount per eligible dependent.
        return total_eligible_dependents * p.amount
