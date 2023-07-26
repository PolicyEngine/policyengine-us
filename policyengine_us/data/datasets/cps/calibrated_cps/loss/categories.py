from .utils import NationalMetric

class EmploymentIncome(NationalMetric):
    policyengine_variable = "employment_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.employment_income"

class AdjustedGrossIncome(NationalMetric):
    policyengine_variable = "adjusted_gross_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.adjusted_gross_income"

class TaxableInterestIncome(NationalMetric):
    policyengine_variable = "taxable_interest_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.taxable_interest_income"

class TaxExemptInterestIncome(NationalMetric):
    policyengine_variable = "tax_exempt_interest_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.tax_exempt_interest_income"

class NonQualifiedDividendIncome(NationalMetric):
    policyengine_variable = "non_qualified_dividend_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.non_qualified_dividend_income"

class QualifiedDividendIncome(NationalMetric):
    policyengine_variable = "qualified_dividend_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.qualified_dividend_income"

class SelfEmploymentIncome(NationalMetric):
    policyengine_variable = "self_employment_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.self_employment_income"

class CapitalGains(NationalMetric):
    policyengine_variable = "capital_gains"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.capital_gains"

class TaxablePensionIncome(NationalMetric):
    policyengine_variable = "taxable_pension_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.taxable_pension_income"

class PensionIncome(NationalMetric):
    policyengine_variable = "pension_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.pension_income"

class TaxableIncome(NationalMetric):
    policyengine_variable = "taxable_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.taxable_income"


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
