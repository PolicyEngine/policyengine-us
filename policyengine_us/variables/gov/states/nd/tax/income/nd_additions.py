from policyengine_us.model_api import *


class nd_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota additions to federal taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1"  # line 5
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1"  # line 5
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14"
    )
    defined_for = StateCode.ND
    adds = "gov.states.nd.tax.income.taxable_income.additions.sources"
