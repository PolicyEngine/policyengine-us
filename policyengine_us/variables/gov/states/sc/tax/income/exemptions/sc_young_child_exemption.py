from policyengine_us.model_api import *


class sc_young_child_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina young child exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf"
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        # Get relevant parameter subtree.
        p = parameters(period).gov.states.sc.tax.income.exemptions.young_child
        # Determine eligibility for each person in the tax unit.
        person = tax_unit.members
        meets_age_limit = person("age", period) < p.ineligible_age
        eligible = meets_age_limit & person("is_tax_unit_dependent", period)
        # Count number of eligible people in the tax unit.
        count_eligible = tax_unit.sum(eligible)
        # Multiply by the amount per exemption.
        return count_eligible * p.amount
