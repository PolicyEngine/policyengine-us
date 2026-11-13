from policyengine_us.model_api import *


class or_federal_tax_liability_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR federal tax liability subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        # ORS 316.680(1)(b), 316.685 and 316.695(3).
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",
        # ORS 316.680(1)(b) and 316.685(1), 2023 edition, PDF pages 52 and 54.
        "https://www.oregonlegislature.gov/bills_laws/Archive/2023ors316.pdf#page=52",
        # 26 U.S.C. 1411(a)(1): the net investment income tax is imposed
        # under Subtitle A.
        "https://www.law.cornell.edu/uscode/text/26/1411#a_1",
        # Publication OR-17, federal tax worksheet, Part A, the premium tax
        # credit line (line 7, from 2025 line 8; 2021 line 11) and the 2021
        # credit lines 2 and 8 to 13.
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2017.pdf#page=63",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2018.pdf#page=68",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2019.pdf#page=63",
        # PDF pages 65-66
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2020.pdf#page=65",
        # PDF pages 72-73
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=72",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2022.pdf#page=73",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2023.pdf#page=73",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2024.pdf#page=71",
        # PDF pages 71-72
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2025.pdf#page=71",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.subtractions.federal_tax_liability
        )
        # Federal tax after nonrefundable credits plus the other taxes in
        # income_tax_before_refundable_credits. The net investment income tax
        # stays in: it is imposed under Subtitle A (26 U.S.C. 1411(a)(1)), and
        # ORS 316.685(3) does not exclude it. The employee Social Security and
        # Medicare tax on unreported tips and wages comes out (ORS
        # 316.685(3)(a)).
        federal_tax = tax_unit(
            "income_tax_before_refundable_credits", period
        ) - tax_unit("unreported_payroll_tax", period)
        # Every federal refundable credit except the earned income credit
        # reduces the liability (ORS 316.685(1)(b)), and so does the premium
        # tax credit (Form 8962, line 24), which the federal list omits. Read
        # the federal total, income_tax_refundable_credits, rather than the
        # list, so credits that structural reforms add to that variable count
        # too; back out the EITC only when the list carries it. The federal
        # list, and so the total, includes the section 1341(a)(5) credit
        # (claim_of_right_credit). Relief under section 1341(a)(4), an
        # itemized deduction, already lowers
        # income_tax_before_refundable_credits. Either way, section 1341
        # relief reduces the liability.
        refundable = parameters(period).gov.irs.credits.refundable
        eitc = tax_unit("eitc", period) if "eitc" in refundable else 0
        refundable_credits = (
            tax_unit("income_tax_refundable_credits", period)
            - eitc
            + tax_unit("assigned_aca_ptc", period)
        )
        or_federal_income_tax = max_(0, federal_tax - refundable_credits)
        # limit subtraction based on caps scaled to federal AGI
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        federal_agi = tax_unit("adjusted_gross_income", period)
        cap = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.cap.single.calc(federal_agi),
                p.cap.joint.calc(federal_agi),
                p.cap.head_of_household.calc(federal_agi),
                p.cap.separate.calc(federal_agi),
                p.cap.surviving_spouse.calc(federal_agi),
            ],
        )
        return min_(or_federal_income_tax, cap)
