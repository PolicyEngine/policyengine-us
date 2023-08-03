from policyengine_us.model_api import *


class nd_rtrc(Variable):
    value_type = float
    entity = TaxUnit
    label = "ND resident-tax-relief nonrefundable credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2021-individual-income-tax-booklet.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2022.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2022-individual-income-tax-booklet.pdf"
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.income.credits
        filing_status = tax_unit("filing_status", period)
        rtrc_amount = where(
            filing_status == filing_status.possible_values.JOINT,
            p.resident_tax_relief.joint_amount,
            p.resident_tax_relief.other_amount,
        )
        inctax = tax_unit("nd_income_tax_before_credits", period)
        return min_(rtrc_amount, inctax)
