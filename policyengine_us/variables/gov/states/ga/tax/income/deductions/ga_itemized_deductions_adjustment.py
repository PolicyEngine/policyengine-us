from policyengine_us.model_api import *


class ga_itemized_deductions_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia itemized deductions adjustment"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.GA
    # Georgia-specific reduction from federal Schedule A before computing
    # Georgia itemized deductions. Remains an explicit input because the
    # baseline microdata do not separately observe components such as
    # other-state income taxes and exempt-income investment interest.
    reference = (
        "https://law.justia.com/codes/georgia/2024/title-48/chapter-7/article-2/section-48-7-27/",
        "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=16",
    )
