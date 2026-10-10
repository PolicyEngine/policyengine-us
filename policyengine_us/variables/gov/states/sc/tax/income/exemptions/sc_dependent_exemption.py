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
        # Section 12-6-1140(13): "each dependent must meet the eligibility
        # requirements of Section 151 and 152", and under IRC 152(b)(1) a
        # return on which the filer (or, if joint, either spouse) can be
        # claimed as a dependent has no dependents.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents = where(
            filer_is_dependent, 0, tax_unit("tax_unit_dependents", period)
        )
        # Multiply by the amount per exemption.
        return dependents * p.amount
