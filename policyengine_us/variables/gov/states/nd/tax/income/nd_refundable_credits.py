from policyengine_us.model_api import *


class nd_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "ND refundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2021-individual-income-tax-booklet.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2022.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2022-individual-income-tax-booklet.pdf"
    )
    defined_for = StateCode.ND
    # adds = "gov.states.nd.tax.income.credits.refundable"  # ND has none
