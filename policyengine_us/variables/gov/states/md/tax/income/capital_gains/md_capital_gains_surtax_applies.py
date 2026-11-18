from policyengine_us.model_api import *


class md_capital_gains_surtax_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maryland capital gains surtax applies"
    definition_period = YEAR
    documentation = (
        "Whether federal adjusted gross income is more than the threshold, "
        "the test in Md. Code, Tax-General 10-105(a)(4) and Form 502 line 1. "
        "The threshold is on federal, not Maryland, adjusted gross income, "
        "and is the same for every filing status."
    )
    reference = [
        dict(
            title="Md. Code, Tax-General § 10-105(a)(4)",
            href="https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-105&enactments=false",
        ),
        dict(
            title="2025 Md. Laws ch. 604 (HB 352), § 3, amending Tax-General § 10-105(a)(4)",
            href="https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=164",
        ),
        dict(
            title="2025 Maryland Form 502CG instructions, general instructions",
            href="https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/502cg.pdf#page=2",
        ),
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.capital_gains
        if not p.surtax_applies:
            return False
        federal_agi = tax_unit("adjusted_gross_income", period)
        return federal_agi > p.surtax_threshold
