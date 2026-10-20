from policyengine_us.model_api import *


class id_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    documentation = (
        "Idaho other subtractions from federal adjusted gross income reported on "
        "Form 40, Line 22 (Other subtractions), entered as a positive amount. "
        "Do not include state tax refunds, U.S. government interest, military pay/retirement, "
        "Social Security, dependent care, retirement/aged deductions, capital gains, "
        "workers' compensation, 529 contributions, or health insurance, which PolicyEngine computes separately."
    )
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=15"
