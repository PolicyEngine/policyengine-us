from policyengine_us.model_api import *


class sc_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina dependent exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf#page=2",
        "https://www.scstatehouse.gov/code/t12c006.php",
        # SECTION 12-6-1140 (13)
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        # Get relevant parameter subtree. The amount for dependent exemption is the same amount as the the young_child's.
        p = parameters(period).gov.states.sc.tax.income.deductions.young_child
        # every dependent is eligible
        dependents = tax_unit("tax_unit_dependents", period)
        # Multiply by the amount per exemption.
        return dependents * p.amount
