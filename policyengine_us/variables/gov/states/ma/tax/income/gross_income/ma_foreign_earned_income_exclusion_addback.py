from policyengine_us.model_api import *


class ma_foreign_earned_income_exclusion_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA addition of foreign earned income excluded under section 911"
    unit = USD
    documentation = (
        "Foreign earned income and housing amounts excluded from federal gross "
        "income under 26 U.S.C. 911(a), which Massachusetts adds to gross "
        "income: Form 2555 line 43 (the line 36 housing exclusion plus the "
        "line 42 foreign earned income exclusion, from both spouses' forms on a "
        "joint return). It is not reduced by the line 44 deductions allocable "
        "to the excluded income or by Foreign Earned Income Tax Worksheet line "
        "2b, and it does not include the line 50 housing deduction, which is a "
        "deduction rather than an exclusion. Other income inputs must already "
        "exclude this amount. When any section 911 leaf input is supplied for "
        "the year or carried from an earlier year, the default is "
        "foreign_earned_income_exclusion_gross, floored at zero. For legacy "
        "callers supplying no applicable leaves, the default "
        "remains foreign_earned_income_exclusion, the worksheet line 2c "
        "stacking amount, floored at zero. That legacy approximation equals "
        "line 43 when Form 2555 lines 44 and 50 and worksheet line 2b are "
        "zero, or when line 50 equals line 44 plus line 2b. An entered "
        "Massachusetts amount, including zero, replaces either default."
    )
    definition_period = YEAR
    reference = (
        # c.62 s.2(a)(1)(C): "Earned income from foreign sources excluded
        # under section nine hundred and eleven of the Code" is added to
        # federal gross income.
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",
        # Form 1 line 3: compensation excluded under IRC s.911 must be
        # included in line 3 for Massachusetts tax purposes.
        "https://www.mass.gov/doc/2025-form-1-instructions/download#page=10",
        # Form 2555 Part VIII, line 43: lines 36 and 42, before line 44.
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
        # Foreign Earned Income Tax Worksheet lines 2a to 2c.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=37",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        leaf_inputs = [
            "foreign_earned_income_exclusion_amount",
            "foreign_housing_exclusion",
            "foreign_earned_income_exclusion_allocable_deductions",
            "foreign_housing_deduction",
            "foreign_earned_income_exclusion_disallowed_deductions",
        ]
        # Core's input export helper tracks supplied values by year and
        # branch. Cached default zeros must not replace the legacy fallback;
        # explicitly supplied zeros must. Available since core 3.32.8.
        if any(
            input_period.start <= period.start
            for variable in leaf_inputs
            for input_period in tax_unit.simulation._get_exportable_input_periods(
                variable, include_computed_variables=False
            )
        ):
            return max_(0, tax_unit("foreign_earned_income_exclusion_gross", period))
        return max_(0, tax_unit("foreign_earned_income_exclusion", period))
