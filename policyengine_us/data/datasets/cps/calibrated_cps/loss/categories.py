from .utils import NationalMetric


class EmploymentIncome(NationalMetric):
    policyengine_variable: str = "employment_income"
    parameter_name: str = (
        "us.programs.federal_income_tax.sources_of_income.employment_income"
    )


class AdjustedGrossIncome(NationalMetric):
    policyengine_variable: str = "adjusted_gross_income"
    parameter_name: str = "us.programs.federal_income_tax.sources_of_income.adjusted_gross_income"


class IncomeTax(NationalMetric):
    policyengine_variable: str = "income_tax"
    parameter_name: str = "us.programs.federal_income_tax.budgetary_impact"


class SNAP(NationalMetric):
    policyengine_variable: str = "snap"
    parameter_name: str = "us.programs.snap.budgetary_impact"


class SocialSecurity(NationalMetric):
    policyengine_variable: str = "social_security"
    parameter_name: str = "us.programs.social_security.total.budgetary_impact"


class SSI(NationalMetric):
    policyengine_variable: str = "ssi"
    parameter_name: str = "us.programs.ssi.budgetary_impact"


class Population(NationalMetric):
    policyengine_variable: str = "household_count_people"
    parameter_name: str = "us.populations.people.total"
