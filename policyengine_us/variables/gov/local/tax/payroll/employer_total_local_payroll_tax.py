from policyengine_us.model_api import *


class employer_total_local_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total local payroll tax"
    documentation = (
        "Employer-level local and regional payroll tax liability from "
        "aggregate employer inputs."
    )
    definition_period = YEAR
    unit = USD
    adds = [
        "ny_mctmt_total_employer_tax",
        "co_denver_total_business_occupational_privilege_tax",
        "co_glendale_total_business_occupational_privilege_tax",
        "co_greenwood_village_total_business_occupational_privilege_tax",
        "co_sheridan_total_business_occupational_privilege_tax",
        "mo_st_louis_total_payroll_expense_tax",
        "or_trimet_total_payroll_tax",
        "or_lane_transit_district_total_payroll_tax",
        "wa_seattle_total_payroll_expense_tax",
        "wa_seattle_total_social_housing_tax",
    ]
