from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.filer_schedule_d_lines import (
    filer_schedule_d_lines,
)


class filer_loss_limited_net_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer's loss-limited net capital gains"
    unit = USD
    documentation = (
        "Form 1040 line 7a of the head and spouse: their Schedule D net "
        "capital gain or loss, including capital gain distributions (line "
        "13), with a net loss limited under 26 USC 1211(b). This is Form 8960 "
        "line 5a without Schedule 1 line 4. A tax unit dependent's gains and "
        "losses are on the dependent's own return. Unlike "
        "loss_limited_net_capital_gains, this leaves dependents out. It "
        "uses the same filer Schedule D lines as the tax worksheet. A tax "
        "unit net_capital_gains amount supplied as an input "
        "is kept; that amount is read as covering every member, and any "
        "dependent's person-level gains and losses are then taken out."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        loss_limit = p.capital_gains.loss_limit[filing_status]
        lines = filer_schedule_d_lines(tax_unit, period)
        return max_(-loss_limit, lines.line_16)
