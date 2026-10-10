from policyengine_us.model_api import *


class md_capital_gains_surtax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland capital gains surtax"
    definition_period = YEAR
    unit = USD
    documentation = (
        "The additional 2% tax on net capital gain included in Maryland "
        "adjusted gross income, less the gain from excepted assets, for a "
        "filer with federal adjusted gross income over $350,000. Form 502 "
        "line 21b: Form 502CG line 9 (line 1 less line 8, not below zero) "
        "times 2%."
    )
    reference = [
        dict(
            title="Md. Code, Tax-General § 10-105(a)(3) and (4)",
            href="https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-105&enactments=false",
        ),
        dict(
            title="2025 Md. Laws ch. 604 (HB 352), § 3, amending Tax-General § 10-105(a)",
            href="https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=163",
        ),
        dict(
            title="2025 Maryland Form 502CG, line 9",
            href="https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/502cg.pdf#page=1",
        ),
        dict(
            title="2025 Maryland Resident Income Tax Instructions, lines 20a and 21b",
            href="https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=21",
        ),
    ]
    defined_for = "md_capital_gains_surtax_applies"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.capital_gains
        # Form 502CG line 1: net capital gain included in Maryland AGI.
        net_capital_gain = tax_unit("md_net_capital_gain", period)
        # Line 8: the part from excepted assets (lines 2 through 7).
        excepted = tax_unit("md_capital_gains_surtax_excepted_gain", period)
        # Line 9, carried to Form 502 line 20a.
        subject_to_surtax = max_(0, net_capital_gain - excepted)
        return subject_to_surtax * p.surtax_rate
