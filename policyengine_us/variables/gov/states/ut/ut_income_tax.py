from policyengine_us.model_api import *

FORM = """
2 a) dependents 16 and under
b) dependents 17 and older
c) total
4 Federal adjusted gross income from federal return
5 Additions to income from TC-40A, Part 1 (attach TC-40A, page 1)
6 Total income - add line 4 and line 5
7 State tax refund included on federal form 1040, Schedule 1, line 1 (if any)
8 Subtractions from income from TC-40A, Part 2 (attach TC-40A, page 1)
9 Utah taxable income/loss - subtract the sum of lines 7 and 8 from line 6
10 Utah tax - multiply line 9 by 4.85% (.0485) (not less than zero)
11 Utah personal exemption (multiply line 2c by $1,802) •11
12 Federal standard or itemized deductions • 12
13 Add line 11 and line 12 13
14 State income tax included in federal itemized deductions • 14
15 Subtract line 14 from line 13 15
16 Initial credit before phase-out - multiply line 15 by 6% (.06) • 16
17 Enter: $15,548 (if single or married filing separately); $23,322 (if head • 17 of household); or $31,096 (if married filing jointly or qualifying widower)
18 Income subject to phase-out - subtract line 17 from line 9 (not less than zero) 18
19 Phase-out amount - multiply line 18 by 1.3% (.013) • 19
20 Taxpayer tax credit - subtract line 19 from line 16 (not less than zero)
21 If you are a qualified exempt taxpayer, enter “X” (complete worksheet in instr.) • 21
22 Utah income tax - subtract line 20 from line 10 (not less than zero)
23 Enter tax from TC-40, page 1, line 22
24 Apportionable nonrefundable credits from TC-40A, Part 3 (attach TC-40A, page 1)
25 Full-year resident, subtract line 24 from line 23 (not less than zero). Non or Part-year resident, complete and enter the UTAH TAX from TC-40B, line 41
26 Nonapportionable nonrefundable credits from TC-40A, Part 4 (attach TC-40A, page 1)
27 Subtract line 26 from line 25 (not less than zero)
28 Voluntary contributions from TC-40, page 3, Part 4 (attach TC-40, page 3)
29 AMENDED RETURN ONLY - previous refund
30 Recapture of low-income housing credit
31 Utah use tax
32 Total tax, use tax and additions to tax (add lines 27 through 31)
33 Utah income tax withheld shown on TC-40W, Part 1 (attach TC-40W, page 1)
34 Credit for Utah income taxes prepaid from TC-546 and 2021 refund applied to 2022
35 Pass-through entity withholding tax shown on TC-40W, Part 3 (attach TC-40W, page 2)
36 Mineral production withholding tax shown on TC-40W, Part 2 (attach TC-40W, page 2)
37 AMENDED RETURN ONLY - previous payments
38 Refundable credits from TC-40A, Part 5 (attach TC-40A, page 2)
39 Total withholding and refundable credits - add lines 33 through 38
40 TAX DUE - subtract line 39 from line 32 (not less than zero)
41 Penalty and interest (see instructions)
42 TOTAL DUE - PAY THIS AMOUNT - add line 40 and line 41
43 REFUND - subtract line 32 from line 39 (not less than zero)
"""

# Copilot INSTRUCTION: below, add an OpenFisca variable for each line of the form.


class ut_dependents_under_17(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah dependents under 17"
    unit = USD
    documentation = "Form TC-40, line 2a"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_tax_unit_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        return tax_unit.sum(is_tax_unit_dependent * (age < 17))


class ut_dependents_over_17(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah dependents over 17"
    unit = USD
    documentation = "Form TC-40, line 2b"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_tax_unit_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        return tax_unit.sum(is_tax_unit_dependent * (age >= 17))


class ut_total_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah total dependents"
    unit = USD
    documentation = "Form TC-40, line 2c"
    definition_period = YEAR
    defined_for = StateCode.UT
    adds = ["ut_dependents_under_17", "ut_dependents_over_17"]


class ut_additions_to_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah additions to income"
    unit = USD
    documentation = "Form TC-40, line 5"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"


class ut_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah total income"
    unit = USD
    documentation = "Form TC-40, line 6"
    definition_period = YEAR
    defined_for = StateCode.UT
    adds = ["adjusted_gross_income", "ut_additions_to_income"]


class ut_state_tax_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah state tax refund"
    unit = USD
    documentation = "Form TC-40, line 7"
    definition_period = YEAR
    defined_for = StateCode.UT
    adds = ["salt_refund_last_year"]


class ut_subtractions_from_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah subtractions from income"
    unit = USD
    documentation = "Form TC-40, line 8"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"


class ut_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxable income"
    unit = USD
    documentation = "Form TC-40, line 9"
    definition_period = YEAR
    adds = ["ut_total_income"]
    defined_for = StateCode.UT
    subtracts = ["ut_subtractions_from_income", "ut_state_tax_refund"]


class ut_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT


class ut_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax before credits"
    unit = USD
    defined_for = StateCode.UT
    documentation = "Form TC-40, line 10"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ut_taxable_income = tax_unit("ut_taxable_income", period)
        total_tax = (
            ut_taxable_income
            * parameters(period).gov.states.ut.tax.income.rate
        )
        return max_(total_tax, 0)


class ut_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah personal exemption"
    unit = USD
    defined_for = StateCode.UT
    documentation = "Form TC-40, line 11"
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"

    def formula(tax_unit, period, parameters):
        ut_total_dependents = tax_unit("ut_total_dependents", period)
        rate = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.personal_exemption
        return rate * ut_total_dependents


class ut_federal_deductions_for_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah federal deductions considered for taxpayer credit"
    unit = USD
    documentation = "These federal deductions are added to the Utah personal exemption to determine the Utah taxpayer credit."
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"

    def formula(tax_unit, period, parameters):
        federal_itemizing = tax_unit("tax_unit_itemizes", period)
        p = parameters(period).gov.irs.deductions
        items = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        federal_itemized_deductions_less_salt = add(tax_unit, period, items)
        standard_deduction = tax_unit("standard_deduction", period)
        return where(
            federal_itemizing,
            federal_itemized_deductions_less_salt,
            standard_deduction,
        )


class ut_taxpayer_credit_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah initial taxpayer credit"
    unit = USD
    documentation = "Form TC-40, line (12 through) 16"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        deductions = add(
            tax_unit,
            period,
            [
                "ut_personal_exemption",
                "ut_federal_deductions_for_taxpayer_credit",
            ],
        )
        rate = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.rate
        # The exemption is not actually applied here in the form, but we include it here
        # to avoid counting the exemption as a nonrefundable credit when comparing against
        # ut_income_tax_before_credits.
        return rate * deductions


class ut_taxpayer_credit_phase_out_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxpayer credit phase-out income"
    unit = USD
    documentation = (
        "Income that reduces the Utah taxpayer credit. Form TC-40, line 18"
    )
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        thresholds = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.phase_out.threshold
        threshold = thresholds[filing_status]
        income = tax_unit("ut_taxable_income", period)
        return max_(income - threshold, 0)


class ut_taxpayer_credit_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxpayer credit reduction"
    unit = USD
    documentation = "Form TC-40, line 19"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        phase_out_income = tax_unit(
            "ut_taxpayer_credit_phase_out_income", period
        )
        phase_out_rate = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.phase_out.rate
        return phase_out_income * phase_out_rate


class ut_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxpayer credit"
    unit = USD
    documentation = "Form TC-40, line 20"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        initial_credit = tax_unit("ut_taxpayer_credit_max", period)
        reduction = tax_unit("ut_taxpayer_credit_reduction", period)
        return max_(initial_credit - reduction, 0)


class ut_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "exempt from Utah income tax"
    unit = USD
    documentation = "Form TC-40, line 21"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        basic_standard_deduction = tax_unit("basic_standard_deduction", period)
        return federal_agi <= basic_standard_deduction


class ut_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ut_income_tax_before_credits = tax_unit(
            "ut_income_tax_before_credits", period
        )
        ut_taxpayer_credit = tax_unit("ut_taxpayer_credit", period)
        return max_(ut_income_tax_before_credits - ut_taxpayer_credit, 0)


class ut_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    adds = ["ut_income_tax_before_credits"]
    defined_for = StateCode.UT
