from policyengine_us.model_api import *


class ok_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma gross income used in OK credit calculations"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        # compute comprehensive gross income for all people in tax unit
        p = parameters(period).gov.states.ok.tax.income
        income = 0
        for source in p.credits.gross_income_sources:
            # gross income includes only positive amounts (i.e., no losses)
            income += max_(0, add(tax_unit, period, [source]))
        return income
