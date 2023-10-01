from policyengine_us.model_api import *


class ky_pension_income_exclusion(Variable):
    value_type = float
    entity = Person
    label = "KY Pension Income Exclusion"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        # Get the KY pension income exclusion parameter tree.
        p = parameters(
            period
        ).gov.states.ky.tax.income.exclusions.pension_income

        # Get taxable pension and retirement income.
        pension_income = person("taxable_pension_income", period)

        # Check if person is eligible for exemption.
        exemption_eligible = person(
            "ky_pension_income_exclusion_exemption_eligible", period
        )

        # Get the share of service credit months worked before 1998.
        exemption_percentage = person(
            "ky_service_credits_percentage_pre_1998", period
        )

        # Get the exempt amount, based on eligibility and share of months worked pre-1998.
        exempt_amount = (
            exemption_eligible * exemption_percentage * pension_income
        )
        non_exempt_amount = pension_income - exempt_amount

        # Get retirement income not already exempt.
        other_income = (
            add(person, period, p.other_retirement_income_sources)
            + non_exempt_amount
        )

        # Apply cap (towards just other income if exemption eligible).
        return where(
            exemption_eligible,
            exempt_amount + min_(other_income, p.threshold),
            min_(pension_income + other_income, p.threshold),
        )
