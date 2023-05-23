from .utils import NationalMetric

class EmploymentIncome(NationalMetric):
    policyengine_variable: str = "employment_income"
    policyengine_entity: str = "person"
    parameter_name: str = "us.programs.federal_income_tax.sources_of_income.employment_income"
    should_sum_by_household: bool = True

class Population(NationalMetric):
    policyengine_variable: str = "age"
    policyengine_entity: str = "person"
    parameter_name: str = "us.populations.people.total"
    is_nonzero_count: bool = True
    should_sum_by_household: bool = False
