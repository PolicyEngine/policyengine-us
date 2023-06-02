from policyengine_us.model_api import *


class sc_senior_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina senior exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf"
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the SC senior exemptions part of the parameter tree
        p = parameters(period).gov.states.sc.tax.income.exemptions.senior

        # Get the individual filer's age.
        age_head = tax_unit("age_head", period)

        # Determine if head of household (filer) is eligible.
        head_eligible = (age_head >= p.age_threshold).astype(int)

        # Get the spouse age, if applicable.
        age_spouse = tax_unit("age_spouse", period)

        # Determine whether spouse is eligible (>= age 65).
        joint = filing_status == filing_status.possible_values.JOINT
        spouse_eligible = ((age_spouse >= p.age_threshold) * joint).astype(int)

        # Get SC retirement income deduction and military retirement income deduction
        retirement_income_deduction = tax_unit(
            "sc_retirement_income_deduction", period
        )
        retirement_income_deduction_spouse = tax_unit(
            "sc_retirement_income_deduction_spouse", period
        )
        sc_military_retirement_income_deduction = tax_unit(
            "sc_military_retirement_income_deduction", period
        )
        sc_military_retirement_income_deduction_spouse = tax_unit(
            "sc_military_retirement_income_deduction_spouse", period
        )

        # Calculate senior exemption. The exemption can not be less than 0. Add head and spouse together.
        return max(
            head_eligible * p.amount
            - retirement_income_deduction
            - sc_military_retirement_income_deduction,
            0,
        ) + max(
            spouse_eligible * p.spouse_amount
            - retirement_income_deduction_spouse
            - sc_military_retirement_income_deduction_spouse,
            0,
        )
