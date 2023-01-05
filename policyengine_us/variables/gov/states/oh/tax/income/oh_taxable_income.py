from policyengine_us.model_api import *


class oh_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "OH taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf"
    defined_for = StateCode.OH
