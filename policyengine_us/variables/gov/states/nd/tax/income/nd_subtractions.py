from policyengine_us.model_api import *


class nd_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ND subtractions from federal taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2021-individual-income-tax-booklet.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2022.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2022-individual-income-tax-booklet.pdf"
    )
    defined_for = StateCode.ND
    adds = "gov.states.nd.tax.income.taxable_income.subtractions.sources"
