from policyengine_us.model_api import *


class sc_senior_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "South Carolina senior exemption for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf"
    defined_for = StateCode.SC

    def formula(person, period, parameters):
        # Get the SC senior exemptions part of the parameter tree
        p = parameters(period).gov.states.sc.tax.income.exemptions.senior

        # Get the individual filer's age.
        age = person("age", period)

        # Determine if head of household (filer) is eligible.
        age_eligible = age >= p.age_threshold

        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        eligible = head_or_spouse & age_eligible
        # Get SC retirement income deduction and military retirement income deduction

        total_deductions = add(
            person,
            period,
            [
                "sc_retirement_deduction_indv",
                "sc_military_deduction_indv",
            ],
        )

        # Calculate senior exemption. The exemption can not be less than 0.
        reduced_max_amount = max_(p.amount - total_deductions, 0)

        return eligible * reduced_max_amount
