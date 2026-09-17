from policyengine_us.model_api import *


class ok_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma pension subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os68.pdf#page=1012",
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os68.pdf#page=1013",
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2024/511-Pkt-2024.pdf#page=17",
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=17",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.agi.subtractions
        # Get pension and retirement income for each person in the tax unit
        pensions = add(tax_unit.members, period, p.pension_sources)
        # Each person can subtract up to the pension limit
        # Sum across all tax unit members
        return tax_unit.sum(min_(p.pension_limit, pensions))
