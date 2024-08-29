from policyengine_us.model_api import *


class nd_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota nonrefundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=2"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=16"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=2"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=16"
    )
    defined_for = StateCode.ND
    adds = "gov.states.nd.tax.income.credits.nonrefundable"
