from policyengine_us.model_api import *


class qualified_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified business income deduction for tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
    )

    def formula(tax_unit, period, parameters):
        # compute sum of QBID amounts for each person in TaxUnit following
        # logic in 2018 IRS Publication 535, Worksheet 12-A, line 16
        person = tax_unit.members
        qbid_amt = person("qbid_amount", period)
        return tax_unit.sum(qbid_amt)
