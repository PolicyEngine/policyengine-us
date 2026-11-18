from policyengine_us.model_api import *


class mo_st_louis_earnings_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "St. Louis earnings tax"
    documentation = (
        "Net St. Louis earnings tax after optional credits supplied as inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.stlouis-mo.gov/government/departments/collector/"
        "earnings-tax/file-earnings-tax.cfm"
    )
    adds = ["mo_st_louis_earnings_tax_person"]
