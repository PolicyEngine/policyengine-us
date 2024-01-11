from policyengine_us.model_api import *


class oh_insured_unreimbursed_medical_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Ohio insured unreimbursed medical and health care expense deduction"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(10)
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        employer_premium_contribution = person(
            "employer_contribution_to_health_insurance_premiums_category",
            period,
        )
        status = employer_premium_contribution.possible_values
        medicare_eligible = person("is_medicare_eligible", period)
        # Line 3
        eligible_premiums = (
            person("health_insurance_premiums", period) * medicare_eligible
        ) * (employer_premium_contribution == status.NONE)
        # Premiums only count if the employer paid none.
        total_hipaid = tax_unit.sum(eligible_premiums)
        # Line 4
        medical_expenses = add(
            tax_unit, period, ["medical_out_of_pocket_expenses"]
        )
        # Line 5
        total_expenses = total_hipaid + medical_expenses
        # Line 6
        federal_agi = tax_unit("adjusted_gross_income", period)

        # Can deduct medical expenses in excess of 7.5% of federal AGI.
        # Line 7
        rate = parameters(
            period
        ).gov.states.oh.tax.income.deductions.unreimbursed_medical_care_expenses.rate
        agi_floor = federal_agi * rate
        # Line 8
        return max_(0, total_expenses - agi_floor)
