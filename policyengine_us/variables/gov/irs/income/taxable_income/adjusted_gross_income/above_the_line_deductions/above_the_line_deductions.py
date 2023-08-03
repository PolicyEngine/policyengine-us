from policyengine_us.model_api import *


class above_the_line_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Above-the-line deductions"
    unit = USD
    documentation = (
        "Deductions applied to reach adjusted gross income from gross income."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    adds = "gov.irs.ald.deductions"
