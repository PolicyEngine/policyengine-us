from policyengine_us.model_api import *


class md_capital_gains_surtax_excepted_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Maryland net capital gain from assets excepted from the capital gains surtax"
    )
    unit = USD
    documentation = (
        "Net capital gain included in md_net_capital_gain that comes from the "
        "sale or exchange of an asset Md. Code, Tax-General 10-105(a)(3)(ii) "
        "excepts from the additional 2% tax: a primary residence sold for "
        "less than $1,500,000; assets held in a 401(k), 403(b), 457(b), IRA, "
        "Roth IRA or other retirement savings plan; cattle, horses or "
        "breeding livestock held more than 12 months by a taxpayer with more "
        "than half of gross income from farming or ranching; land under a "
        "conservation, agricultural or forest preservation easement; "
        "property used in a trade or business whose cost is deductible under "
        "IRC 179; and affordable housing owned by a nonprofit. Form 502CG "
        "line 8, the sum of lines 2 through 7. Zero unless entered."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="Md. Code, Tax-General § 10-105(a)(3)(ii)",
            href="https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-105&enactments=false",
        ),
        dict(
            title="Maryland Comptroller Technical Bulletin No. 58 (Dec. 29, 2025), sections II and III.A",
            href="https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/technical-bulletins/tb-58.pdf#page=1",
        ),
        dict(
            title="2025 Maryland Form 502CG, lines 2 through 8",
            href="https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/502cg.pdf#page=1",
        ),
    ]
    defined_for = StateCode.MD
