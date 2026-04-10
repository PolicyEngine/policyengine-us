from policyengine_us.model_api import *


class filer_meets_ctc_identification_requirements(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer meets CTC or ODC identification requirements"
    reference = "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_tin = person("has_tin", period)
        # The combined CTC/ODC is unavailable if any filer lacks an SSN or ITIN.
        return tax_unit.all(~head_or_spouse | has_tin)
