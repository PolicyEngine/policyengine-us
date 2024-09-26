from policyengine_us.model_api import *


class in_other_add_backs(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana other add backs"
    definition_period = YEAR
    documentation = "Other add backs including those for Conformity, Employer Student Loan Payment, Meal Deductions, Student Loan Discharges, Excess Federal Interest Deduction Modification, Federal Repatriated Dividend Deductions, Qualified Preferred Stock, and Catch-Up Modifications."
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"
    )
    # use federal variables if they are added later
    defined_for = StateCode.IN
