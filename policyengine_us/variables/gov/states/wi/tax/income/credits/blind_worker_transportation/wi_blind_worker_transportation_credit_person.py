from policyengine_us.model_api import *


class wi_blind_worker_transportation_credit_person(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin blind-worker transportation credit per claimant"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    documentation = (
        "Claimant-limited credit before the tax-unit liability limit, assuming "
        "a timely claim. The supplied is_blind status must meet IRC 63(f)(4). "
        "Qualified expenses establish the paid work commute; no positive-income "
        "test applies. A spouse qualifies on this return only when filing jointly."
    )
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71.pdf#page=56",
        # PDF pages 17-18.
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=17",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partI-sec63.htm",
    )

    def formula_2024_01_01(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wi.tax.income.credits.blind_worker_transportation
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        claimant = head | (spouse & joint)
        blind = person("is_blind", period)
        expenses = person("wi_blind_worker_qualifying_transportation_expenses", period)
        credit = min_(p.max_amount, p.rate * max_(expenses, 0))
        return credit * claimant * blind
