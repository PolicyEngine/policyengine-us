from policyengine_us.model_api import *


class nc_scca_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance program countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/FINAL-Chapter-7-Family-definition-and-determining-income-eligibility-08-05-24.pdf#page=11"
    defined_for = StateCode.NC
    adds = "gov.states.nc.ncdhhs.scca.income.sources"
