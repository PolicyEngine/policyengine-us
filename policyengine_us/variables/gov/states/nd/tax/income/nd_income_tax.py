from policyengine_us.model_api import *


class nd_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf"
    )
    defined_for = StateCode.ND
    adds = ["nd_income_tax_before_refundable_credits"]
    subtracts = ["nd_refundable_credits"]
