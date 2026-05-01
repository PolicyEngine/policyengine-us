from policyengine_us.model_api import *


class me_income_tax_surcharge(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine income tax surcharge"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=220"

    def formula(tax_unit, period, parameters):
        # Sec. DDDD-2 also extends the surcharge to estates and trusts at the
        # single-filer rate; PolicyEngine does not model estates or trusts.
        p = parameters(period).gov.states.me.tax.income.surcharge
        taxable_income = tax_unit("me_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        threshold = p.threshold[filing_status]
        return max_(taxable_income - threshold, 0) * p.rate
