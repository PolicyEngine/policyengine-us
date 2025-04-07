from policyengine_us.model_api import *


class nd_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf"
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        itax_before_credits = tax_unit("nd_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("nd_nonrefundable_credits", period)
        return max_(0, itax_before_credits - nonrefundable_credits)
