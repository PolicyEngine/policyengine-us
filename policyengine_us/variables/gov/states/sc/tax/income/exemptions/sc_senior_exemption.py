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

        head_deductions = add(
            tax_unit,
            period,
            [
                "sc_retirement_income_deduction_head",
                "sc_military_retirement_income_deduction_head",
            ],
        )
        spouse_deductions = add(
            tax_unit,
            period,
            [
                "sc_retirement_income_deduction_spouse",
                "sc_military_retirement_income_deduction_spouse",
            ],
        )

        # Calculate senior exemption. The exemption can not be less than 0. Add head and spouse together.
        # Per the legal code, this applies separately:
        # "(2) In the case of married taxpayers who file a joint federal income tax return, the reduction required by item (1) applies to each individual separately"
        head_exemption = max_(head_eligible * p.amount - head_deductions, 0)
        spouse_exemption = max_(
            spouse_eligible * p.spouse_amount - spouse_deductions, 0
        )
        return head_exemption + spouse_exemption
