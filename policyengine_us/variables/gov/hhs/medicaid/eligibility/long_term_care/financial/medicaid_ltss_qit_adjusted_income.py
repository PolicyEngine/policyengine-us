from policyengine_us.model_api import *


class medicaid_ltss_qit_adjusted_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS QIT-adjusted gross income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Gross monthly income remaining outside qualified income trusts "
        "before Medicaid LTSS income exclusions. The model subtracts each "
        "person's earned and unearned trust deposits from their own gross "
        "source components and combines the remaining income when the "
        "derived assistance unit budgets both spouses as a couple. "
        "Trust legality, irrevocability, funding, payback terms, and the "
        "validity of deposits are unmodeled. Delaware income exclusions "
        "are computed separately in medicaid_ltss_countable_income."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#d_4_B",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=54",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
    )

    def formula(person, period, parameters):
        own_income = person(
            "medicaid_ltss_qit_adjusted_earned_income", period
        ) + person("medicaid_ltss_qit_adjusted_unearned_income", period)
        return where(
            person("medicaid_ltss_assistance_unit_size", period) == 2,
            person.marital_unit.sum(own_income),
            own_income,
        )
