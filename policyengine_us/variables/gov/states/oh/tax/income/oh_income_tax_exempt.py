from policyengine_us.model_api import *


class oh_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "OH income tax exempt"
    defined_for = StateCode.OH
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("oh_taxable_income", period)
        p = parameters(period).gov.states.oh.tax.income
        return taxable_income < p.min_agi_to_pay_tax
