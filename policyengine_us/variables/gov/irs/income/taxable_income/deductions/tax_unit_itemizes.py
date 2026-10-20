from policyengine_us.model_api import *


def choice_branch(tax_unit, period, itemizes):
    """The branch of the simulation in which every tax unit itemizes, or
    every tax unit does not."""
    return get_override_branch(
        tax_unit.simulation,
        "itemizing" if itemizes else "not_itemizing",
        period,
        {"tax_unit_itemizes": np.full(tax_unit.count, itemizes, dtype=bool)},
    )


class tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes tax deductions"
    unit = USD
    documentation = "Whether tax unit elects to itemize deductions rather than claim the standard deduction."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        limitation = p.deductions.itemized.limitation
        if "charitable_contributions_ald" in p.ald.deductions:
            # In 2020 a unit that does not itemize deducts charitable
            # contributions above the line (26 U.S.C. 62(a)(22)), so adjusted
            # gross income depends on the choice, and with it the itemized
            # deductions it limits (the medical floor, the charitable
            # ceiling) and any standard deduction that phases out with it.
            # Each comes from the branch that makes that choice (the ones
            # that also give the tax liabilities compared below).
            itemizing = choice_branch(tax_unit, period, True)
            not_itemizing = choice_branch(tax_unit, period, False)
            itemized_deductions = itemizing.calculate(
                "itemized_taxable_income_deductions", period
            )
            # Not itemizing also lowers adjusted gross income (line 10b, and
            # what follows from it, such as taxable Social Security), so the
            # deductions compared are everything each choice takes from
            # gross income: the standard deduction counts with that
            # reduction.
            agi_reduction = itemizing.calculate(
                "adjusted_gross_income", period
            ) - not_itemizing.calculate("adjusted_gross_income", period)
            standard_deduction = (
                not_itemizing.calculate("standard_deduction", period) + agi_reduction
            )
        elif limitation.applies and limitation.obbb.applies:
            standard_deduction = tax_unit("standard_deduction", period)
            # The itemized deductions the unit would claim if it itemized.
            # The P.L. 119-21 section 68 limitation nets them of the
            # qualified business income deduction, which depends on the
            # itemization choice, so they come from the branch that itemizes
            # (the one that also gives tax_liability_if_itemizing).
            # Calculated before branching, so the branch inherits it.
            tax_unit("total_itemized_taxable_income_deductions", period)
            itemized_deductions = choice_branch(tax_unit, period, True).calculate(
                "itemized_taxable_income_deductions", period
            )
        else:
            standard_deduction = tax_unit("standard_deduction", period)
            itemized_deductions = tax_unit("itemized_taxable_income_deductions", period)
        if parameters(period).gov.simulation.branch_to_determine_itemization:
            # determine federal itemization behavior by comparing tax liability
            tax_liability_if_itemizing = tax_unit("tax_liability_if_itemizing", period)
            tax_liability_if_not_itemizing = tax_unit(
                "tax_liability_if_not_itemizing", period
            )
            # Use a small tolerance for floating-point comparison due to floating point imprecision
            TOLERANCE = 0.01
            federal_tax_equal = (
                np.abs(tax_liability_if_itemizing - tax_liability_if_not_itemizing)
                <= TOLERANCE
            )
            # When federal tax liabilities tie (typical at low/moderate income where
            # refundable credits absorb the tax), fall back to the federal-level
            # deduction comparison. This matches the non-branching path below and
            # the IRS / TaxAct / TAXSIM-comparison default of itemizing whenever
            # itemized deductions exceed the standard deduction.
            return where(
                federal_tax_equal,
                itemized_deductions > standard_deduction,
                tax_liability_if_itemizing < tax_liability_if_not_itemizing,
            )
        # determine federal itemization behavior by comparing deductions
        return itemized_deductions > standard_deduction
