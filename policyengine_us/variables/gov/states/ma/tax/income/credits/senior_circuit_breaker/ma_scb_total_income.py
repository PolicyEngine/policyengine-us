from policyengine_us.model_api import *


class ma_scb_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total income for the MA Senior Circuit Breaker"
    documentation = (
        "M.G.L. c.62 s.6(k)(1) taxpayer's total income: Massachusetts AGI "
        "(Part A, Part B and Part C), increased by the listed income and "
        "receipts to the extent they are excluded or subtracted from AGI, and "
        "reduced by the age 65, blindness and dependent exemptions "
        "(Schedule CB, lines 3 through 9)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section6",  # Subsection (k)(1)
        # PDF pages 1-2: lines 3 to 9 and the line 3 worksheet.
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2025/ma-dor-2025-inc-sch-cb.pdf#page=1",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2025/ma-dor-2025-inc-form-1-inst.pdf#page=30",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # c.62 s.6(k)(1) starts from Part A, Part B and Part C AGI, so the
        # s.2(d) deductions allowed in reaching Part B AGI come off. Schedule
        # CB line 3 worksheet, line 2 subtracts Schedule Y lines 2 to 9b and
        # 10, the lines ma_part_b_agi deducts.
        agi = tax_unit("ma_agi", period)
        # s.6(k)(1) adds back "net capital losses deducted pursuant to
        # paragraph (2) of subsection (c) of section 2" and "net losses in
        # any class of Part C adjusted gross income". Worksheet lines 7 to 10
        # take interest and dividends before any loss (Schedule B line 9) and
        # short-term gains before losses (Schedule B line 15), and lines 12
        # to 18 take long-term gains "not including any losses". So everything
        # Part A and Part C AGI take off those gains is added back: losses
        # applied against dividends (Schedule B lines 20 and 32) and against
        # the other holding period's gains (lines 22 and 25), and the
        # collectibles deduction (line 27), which comes after line 15.
        part_a_gross_income = tax_unit("ma_part_a_gross_income", period)
        long_term_gains = max_(0, tax_unit("ma_long_term_capital_gains", period))
        part_a_and_c_agi = add(tax_unit, period, ["ma_part_a_agi", "ma_part_c_agi"])
        capital_deductions = part_a_gross_income + long_term_gains - part_a_and_c_agi
        scb = parameters(period).gov.states.ma.tax.income.credits.senior_circuit_breaker
        # c.62 s.6(k)(1) adds back amounts excluded or subtracted from the
        # taxpayer's AGI. Dependents' income is never in that AGI, so count
        # only the head's and spouse's person-level amounts.
        disallowed_deductions = tax_unit_non_dep_add(
            tax_unit, period, scb.income.disallowed_deductions
        )

        # Re-add some exemptions
        person = tax_unit.members
        tax = parameters(period).gov.states.ma.tax.income
        blind = person("is_blind", period)
        dependent = person("is_tax_unit_dependent", period)
        count_blind = tax_unit.sum(~dependent & blind)
        blind_exemption = tax.exemptions.blind * count_blind
        # (1C) and (2C): Aged exemptions.
        age = person("age", period)
        count_aged = tax_unit.sum(~dependent & (age >= tax.exemptions.aged.age))
        aged_exemption = tax.exemptions.aged.amount * count_aged
        # (3): Dependent exemptions.
        count_dependents = tax_unit("tax_unit_dependents", period)
        dependent_exemption = tax.exemptions.dependent * count_dependents
        exemptions = blind_exemption + aged_exemption + dependent_exemption

        return max_(0, agi + capital_deductions + disallowed_deductions - exemptions)
