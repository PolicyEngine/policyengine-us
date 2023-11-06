from policyengine_us.model_api import *


class nj_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey CDCC"
    documentation = "New Jersey Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=44"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get New Jersey CDCC rate
        p = parameters(period).gov.states.nj.tax.income.credits.cdcc.rate

        # Get NJ taxable income
        taxable_income = tax_unit("nj_taxable_income", period)

        # Get federal CDCC
        federal_cdcc = tax_unit("cdcc", period)

        # Calculate NJ CDCC
        rate = p.calc(taxable_income, right=True)

        # Calculate total NJ CDCC
        return federal_cdcc * rate
