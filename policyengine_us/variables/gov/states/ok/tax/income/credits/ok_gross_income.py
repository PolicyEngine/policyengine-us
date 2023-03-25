from policyengine_us.model_api import *


class ok_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "OK gross income used in OK credit calculations"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        # compute comprehensive gross income for all people in tax unit
        tax_unit_income_sources = [
            "earned_income_tax_credit",
            "ok_eitc",
        ]
        p = parameters(period).gov.states.ok.tax.income.credits
        person_income_sources = [
            source
            for source in p.gross_income_sources
            if source not in tax_unit_income_sources
        ]
        person = tax_unit.members
        income = 0
        for source in person_income_sources:
            # income includes only positive amounts (i.e., no losses)
            income += max_(0, add(person, period, [source]))
        income += add(tax_unit, period, tax_unit_income_sources)
        return income
