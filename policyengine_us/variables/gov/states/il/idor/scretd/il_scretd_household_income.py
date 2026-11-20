from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.filer_schedule_d_lines import (
    filer_schedule_d_lines,
)


class il_scretd_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Senior Citizens Real Estate Tax Deferral household income"
    unit = USD
    documentation = (
        "Household income under 320 ILCS 30/2(h), which takes the meaning in "
        "the Senior Citizens and Persons with Disabilities Property Tax Relief "
        "Act: the combined income of the claimant and spouse (320 ILCS "
        "25/3.05 and 3.06), where income is federal adjusted gross income "
        "plus the amounts section 3.07 adds back, such as nontaxable Social "
        "Security, SSI, tax-exempt interest, cash public assistance, "
        "workers' compensation and the capital loss carryover deducted."
    )
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/032000300K2.htm",
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/032000250K3.05.htm",
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/032000250K3.06.htm",
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/032000250K3.07.htm",
        "https://cookcountytreasurer.com/pdfs/seniordeferral/IL-1017%20Form%20TY%202025.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.idor.scretd
        ald = parameters(period).gov.irs.ald
        # The household is the claimant and spouse (sections 3.05 and 3.06).
        # Federal AGI already leaves out tax unit dependents' income, and the
        # additions are summed over the head and spouse, except amounts that
        # belong to the filer even when recorded on a dependent, as in
        # above_the_line_deductions. Losses and above-the-line deductions
        # reduce income, as on IL-1017 Worksheet A lines 9 to 13.
        agi = tax_unit("adjusted_gross_income", period)
        additions = tax_unit_non_dep_add(
            tax_unit,
            period,
            p.household_income_additions,
            include_dependents=ald.filer_amounts_recorded_on_dependents,
        )
        # 3.07(G) adds "any net operating loss carryover deduction or capital
        # loss carryover deduction during the taxable year", and IL-1017
        # Worksheet A line 10 (PDF page 2) counts the net capital gain or
        # loss: "Do not include any loss carryover." long_term_capital_gains
        # holds the head's and spouse's long-term carryover as a loss, as
        # Schedule D line 15 does, so AGI is reduced by the part of it that
        # the year's gains absorb or the net loss limit allows. That part is
        # the loss-limited net capital gain without the carryover less the
        # same amount with it; a carryover left unused is not added.
        carryover = max_(
            0,
            tax_unit_non_dep_add(
                tax_unit, period, ["long_term_capital_loss_carryover"]
            ),
        )
        filing_status = tax_unit("filing_status", period)
        loss_limit = ald.loss.capital.max[filing_status]
        net_capital_gain = filer_schedule_d_lines(tax_unit, period).line_16
        carryover_deduction = max_(net_capital_gain + carryover, -loss_limit) - max_(
            net_capital_gain, -loss_limit
        )
        # Not modelled: (B) Illinois income tax paid, which an individual
        # does not deduct in computing AGI; (G) net operating loss and
        # short-term capital loss carryover deductions, which have no input;
        # and the distributions under 35 ILCS 5/203(a)(2)(X) and American
        # Recovery and Reinvestment Act payments that section 3.07 leaves out
        # of income.
        return agi + additions + carryover_deduction
