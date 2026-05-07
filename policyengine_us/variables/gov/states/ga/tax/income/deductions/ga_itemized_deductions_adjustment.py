from policyengine_us.model_api import *


class ga_itemized_deductions_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia itemized deductions adjustment"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.GA
    documentation = (
        "Georgia-specific reduction from federal Schedule A before computing "
        "Georgia itemized deductions. This remains an explicit input because "
        "the model does not separately observe components such as other-state "
        "income taxes and exempt-income investment interest."
    )
    reference = "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download"
