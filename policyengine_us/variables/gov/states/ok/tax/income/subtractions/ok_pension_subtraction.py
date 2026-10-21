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
        # Chart B: filing requirements for dependents
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=5",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.agi.subtractions
        person = tax_unit.members
        # Get pension and retirement income for each person in the tax unit
        pensions = add(person, period, p.pension_sources)
        # Each person can subtract up to the pension limit, but not more than
        # the amount included in federal AGI. Dependents' income is not in
        # federal AGI; they report it on their own return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(min_(p.pension_limit, pensions) * head_or_spouse)
