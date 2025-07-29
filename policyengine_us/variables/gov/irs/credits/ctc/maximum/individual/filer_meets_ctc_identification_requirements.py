from policyengine_us.model_api import *


class filer_meets_ctc_identification_requirements(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer meets CTC identification requirements"

    def formula(tax_unit, period, parameters):
        # Both head and spouse in the tax unit must have valid SSN card type to be eligible for the CTC
        p = parameters(period).gov.irs.credits.ctc
        if p.adult_ssn_requirement_applies:
            person = tax_unit.members
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            eligible_ssn_card_type = person(
                "meets_ctc_identification_requirements", period
            )
            return tax_unit.any(head_or_spouse & eligible_ssn_card_type)
        return True
