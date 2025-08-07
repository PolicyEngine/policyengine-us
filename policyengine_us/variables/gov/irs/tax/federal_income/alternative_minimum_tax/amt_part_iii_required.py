from policyengine_us.model_api import *


class amt_part_iii_required(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax Part III required"
    documentation = "Whether the Alternative Minimum Tax (AMT) Part III worksheet is required, Form 6251, Part III"
    reference = "https://www.irs.gov/pub/irs-pdf/f6251.pdf"

    def formula(tax_unit, period, parameters):
        relevant_inputs = add(
            tax_unit,
            period,
            [
                "dwks10",
                "dwks13",
                "dwks14",
                "dwks19",
                "unrecaptured_section_1250_gain",
            ],
        )
        return relevant_inputs > 0
