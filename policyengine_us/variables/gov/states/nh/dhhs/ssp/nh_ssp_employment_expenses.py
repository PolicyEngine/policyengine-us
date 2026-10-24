from policyengine_us.model_api import *


class nh_ssp_employment_expenses(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire SSP employment expenses"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NH
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = """Employment expenses under He-W 654.18(c)(1): the employee's Federal Insurance Contributions Act taxes. The countable income formula allows at least the regulatory flat amount of He-W 654.18(b) for aged and disabled workers."""
    # NOTE: Expenses in He-W 654.18(c)(2)-(9), such as withholding, are not derived.
    adds = ["employee_social_security_tax", "employee_medicare_tax"]
