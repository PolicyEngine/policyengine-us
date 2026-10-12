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
        # Section 12-6-1140(13): a dependent exemption for every dependent.
        p = parameters(period).gov.states.sc.tax.income.deductions.dependent_exemption
        # every dependent is eligible
        dependents = tax_unit("tax_unit_dependents", period)
        # Multiply by the amount per exemption.
        return dependents * p.amount
