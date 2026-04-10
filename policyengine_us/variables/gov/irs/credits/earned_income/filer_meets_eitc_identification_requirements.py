from policyengine_us.model_api import *


class filer_meets_eitc_identification_requirements(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer meets EITC identification requirements"
    reference = (
        # IRC 32(c)(1)(E) specifies filer and spouse needs a taxpayer identification number.
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_E",
    )

    def formula(tax_unit, period, parameters):
        # Both head and spouse in the tax unit must have valid SSNs to be eligible for the EITC.
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        meets_identification_requirements = person(
            "meets_eitc_identification_requirements", period
        )
        ineligible_head_or_spouse = (
            is_head_or_spouse & ~meets_identification_requirements
        )
        return tax_unit.sum(ineligible_head_or_spouse) == 0
