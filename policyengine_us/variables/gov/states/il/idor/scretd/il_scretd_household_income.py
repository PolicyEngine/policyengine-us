from policyengine_us.model_api import *


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
        "Security, SSI, tax-exempt interest, cash public assistance and "
        "workers' compensation."
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
        # Not modelled: (B) Illinois income tax paid, which an individual
        # does not deduct in computing AGI; (G) net operating loss and
        # capital loss carryover deductions; and the distributions under
        # 35 ILCS 5/203(a)(2)(X) and American Recovery and Reinvestment Act
        # payments that section 3.07 leaves out of income.
        return agi + additions
