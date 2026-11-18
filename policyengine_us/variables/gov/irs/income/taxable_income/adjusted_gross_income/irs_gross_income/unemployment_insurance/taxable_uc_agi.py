from policyengine_us.model_api import *


class taxable_uc_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted gross income for the unemployment compensation exclusion"
    unit = USD
    documentation = (
        "The adjusted gross income IRC 85(c) compares with the cutoff: "
        "adjusted gross income after taxable Social Security and the "
        "above-the-line deductions, without any unemployment compensation "
        "(IRC 85(c)(2)). It is line 6 of the 2020 Unemployment Compensation "
        "Exclusion Worksheet."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/85#c_2",
        # 2020 Instructions for Form 1040 (rev. 4-2021), Unemployment
        # Compensation Exclusion Worksheet, lines 1 through 6.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2020.pdf#page=88",
    )

    def formula(tax_unit, period, parameters):
        irs = parameters(period).gov.irs
        gross_income_sources = irs.gross_income.sources
        # IRC 85(c)(2)(B): without regard to section 85, so without any
        # unemployment compensation. Taxable Social Security, the IRA
        # deduction and the student loan interest and tuition and fees
        # deductions, which this counts (85(c)(2)(A)), are figured with all
        # of it (IRC 86(b)(2)(A), 219(g)(3)(A)(ii), 221(b)(2)(C); 2020
        # Instructions for Form 1040, p. 87, line 7 caution).
        income_sources_without_uc = [
            income_source
            for income_source in gross_income_sources
            if income_source != "taxable_unemployment_compensation"
        ]
        gross_income = 0
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        for source in income_sources_without_uc:
            # Add positive values only - losses are deducted later.
            gross_income += not_dependent * max_(0, add(person, period, [source]))
        gross_income = tax_unit.sum(gross_income)
        above_the_line_deductions = irs.ald.deductions
        # A tax unit dependent's deductions are on their own return.
        total_deductions = tax_unit_non_dep_add(
            tax_unit,
            period,
            above_the_line_deductions,
            include_dependents=irs.ald.filer_amounts_recorded_on_dependents,
        )
        return max_(0, gross_income - total_deductions)
