from policyengine_us.model_api import *


class ok_military_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma military retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        # (g)
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-710-50-15-49",
        # 68 O.S. § 2358(E)(17)
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os68.pdf#page=1017",
        # Schedule 511-A, line 4
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=17",
        # Chart B: filing requirements for dependents
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=5",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ok.tax.income.agi.subtractions.military_retirement
        person = tax_unit.members
        military_retirement_benefits = person("military_retirement_pay", period)
        adjust_military_retirement_amount = military_retirement_benefits * p.rate
        capped_exclusion_amount = max_(p.floor, adjust_military_retirement_amount)
        # Dependents' income is not in federal AGI; they report it on their
        # own return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(
            min_(military_retirement_benefits, capped_exclusion_amount) * head_or_spouse
        )
