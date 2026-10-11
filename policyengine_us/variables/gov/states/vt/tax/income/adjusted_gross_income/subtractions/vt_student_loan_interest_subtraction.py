from policyengine_us.model_api import *


class vt_student_loan_interest_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont student loan interest subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
        "https://legislature.vermont.gov/Documents/2022/Docs/ACTS/ACT138/ACT138%20As%20Enacted.pdf#page=4",
        # Schedule IN-112 lines 16a-16c, form and instructions
        # PDF pages 23, 33
        "https://taxsim.nber.org/historical_state_tax_forms/VT/2025/Income-Booklet-2025.pdf#page=23",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.agi.student_loan_interest
        # 32 V.S.A. 5811(21)(B)(vi) subtracts the interest a qualified resident
        # taxpayer paid on a qualified education loan. Schedule IN-112 line 16
        # subtracts the interest paid (16a) less the amount already deducted
        # on federal Schedule 1 (16b), so interest is not deducted twice. The
        # subtraction has no dependency test of its own: a filer who is
        # claimed elsewhere loses the federal deduction (IRC 221(c)), and
        # Vermont then subtracts the whole amount.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        interest_paid = tax_unit.sum(filer * person("student_loan_interest", period))
        federal_deduction = add(tax_unit, period, ["student_loan_interest_ald"])
        remaining_interest = max_(interest_paid - federal_deduction, 0)
        # 5811(29)(B): a qualified resident taxpayer's adjusted gross income is
        # at most $200,000 if married filing jointly and $120,000 otherwise.
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        income_eligible = agi <= p.income_limit[filing_status]
        return income_eligible * remaining_interest
