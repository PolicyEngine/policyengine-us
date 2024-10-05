from policyengine_us.model_api import *


class oh_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        agi = tax_unit("oh_agi", period)
        exemptions = tax_unit("oh_personal_exemptions", period)

        return max_(0, agi - exemptions)
