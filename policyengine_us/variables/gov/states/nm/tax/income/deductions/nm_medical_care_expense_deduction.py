from policyengine_us.model_api import *


class nm_medical_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico medical care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # 7-2-35. DEDUCTION – UNREIMBURSED OR UNCOMPENSATED MEDICAL CARE EXPENSES
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf#page=249",
        # Tax Form Instructions Page PIT-1-26 LINE 16. Medical Care Expense Deduction
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=31",
        # 7-2-37. Deduction; unreimbursed or uncompensated medical care expenses.
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503888/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcogJQAaZNlKEIARUSFcAT2gBydRIiEwuBIuVrN23fpABlPKQBCagEoBRADKOAagEEAcgGFHE0jAAI2hSdjExIA",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nm.tax.income.deductions.medical_care_expense
        # the deduction amount is based on filing status, agi, and eligible expenses.
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        agi = tax_unit("adjusted_gross_income", period)
        expenses = add(
            tax_unit,
            period,
            ["medical_out_of_pocket_expenses"],
        )
        # Use `right=True` to reflect "over ... but not over ...".
        rate = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
                p.head_of_household.calc(agi, right=True),
                p.separate.calc(agi, right=True),
                p.widow.calc(agi, right=True),
            ],
        )
        return expenses * rate
