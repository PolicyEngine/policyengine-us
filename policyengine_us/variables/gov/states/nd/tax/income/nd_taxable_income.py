from policyengine_us.model_api import *


class nd_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1"  # line 18
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1"  # line 18
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14"
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        us_agi = tax_unit("adjusted_gross_income", period)
        us_ded = tax_unit("taxable_income_deductions", period)
        us_taxinc = us_agi - us_ded  # can be negative per ND instructions
        additions = tax_unit("nd_additions", period)
        subtractions = tax_unit("nd_subtractions", period)
        return max_(0, us_taxinc + additions - subtractions)
