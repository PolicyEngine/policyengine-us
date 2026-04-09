from policyengine_us.model_api import *


class filer_meets_child_ctc_identification_requirements(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer meets child CTC identification requirements"
    reference = "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf"

    def formula(tax_unit, period, parameters):
        filer_meets_tin_requirement = tax_unit(
            "filer_meets_ctc_identification_requirements", period
        )
        p = parameters(period).gov.irs.credits.ctc
        if not p.adult_ssn_requirement_applies:
            return filer_meets_tin_requirement

        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_valid_ssn = person("meets_ctc_identification_requirements", period)
        # For 2025+, at least one filer must have a valid SSN for child CTC.
        return filer_meets_tin_requirement & tax_unit.any(
            head_or_spouse & has_valid_ssn
        )
