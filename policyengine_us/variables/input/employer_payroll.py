from policyengine_us.model_api import *


class employer_state_unemployment_tax_rate_override(Variable):
    value_type = float
    entity = Person
    label = "Employer state unemployment tax rate override"
    documentation = (
        "Optional employer-specific override for the employer-side state "
        "unemployment tax rate. Set to a non-negative rate to replace the "
        "model default."
    )
    unit = "/1"
    definition_period = YEAR
    default_value = -1


class employer_headcount(Variable):
    value_type = int
    entity = Person
    label = "Employer headcount"
    documentation = (
        "Employer employee count used as a proxy for size-based payroll "
        "contribution rules, including paid leave and similar programs."
    )
    definition_period = YEAR
    default_value = 100


class employer_quarterly_payroll_expense_override(Variable):
    value_type = float
    entity = Person
    label = "Employer quarterly payroll expense override"
    documentation = (
        "Optional override for employer quarterly payroll expense used by "
        "payroll-expense taxes such as New York's MCTMT. Set to a non-negative "
        "amount to replace the model proxy."
    )
    unit = USD
    definition_period = YEAR
    default_value = -1


class employer_total_payroll_tax_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total payroll tax gross wages"
    documentation = (
        "Aggregate employer payroll-tax wages for employer-only payroll tax "
        "calculations."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_taxable_earnings_for_social_security(Variable):
    value_type = float
    entity = Person
    label = "Employer total taxable earnings for Social Security"
    documentation = (
        "Aggregate employer taxable earnings under the Social Security wage "
        "base for employer-only payroll tax calculations."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_taxable_earnings_for_federal_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total taxable earnings for federal unemployment tax"
    documentation = (
        "Aggregate employer taxable earnings for FUTA in employer-only "
        "payroll tax calculations."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_taxable_earnings_for_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total taxable earnings for state unemployment tax"
    documentation = (
        "Aggregate employer taxable earnings for state unemployment taxes and "
        "related employer taxes that share that base."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_ny_mctmt_zone_1_quarterly_payroll_expense(Variable):
    value_type = float
    entity = Person
    label = "Employer quarterly MCTMT payroll expense in New York Zone 1"
    documentation = (
        "Aggregate employer quarterly payroll expense in New York MCTMT Zone 1 "
        "for employer-only payroll tax calculations."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_ny_mctmt_zone_2_quarterly_payroll_expense(Variable):
    value_type = float
    entity = Person
    label = "Employer quarterly MCTMT payroll expense in New York Zone 2"
    documentation = (
        "Aggregate employer quarterly payroll expense in New York MCTMT Zone 2 "
        "for employer-only payroll tax calculations."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_co_denver_occupational_privilege_tax_employee_months(Variable):
    value_type = int
    entity = Person
    label = "Employer Denver occupational privilege taxable employee-months"
    documentation = (
        "Annual count of taxable employee-months for Denver's business "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class employer_total_co_denver_occupational_privilege_tax_owner_months(Variable):
    value_type = int
    entity = Person
    label = "Employer Denver occupational privilege owner-months"
    documentation = (
        "Annual count of owner, partner, or manager months subject to "
        "Denver's business occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class employer_total_co_glendale_occupational_privilege_tax_employee_months(Variable):
    value_type = int
    entity = Person
    label = "Employer Glendale occupational privilege taxable employee-months"
    documentation = (
        "Annual count of taxable employee-months for Glendale's employer "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class employer_total_co_glendale_occupational_privilege_tax_owner_months(Variable):
    value_type = int
    entity = Person
    label = "Employer Glendale occupational privilege owner-months"
    documentation = (
        "Annual count of owner, partner, officer, or self-employed months "
        "subject to Glendale's employer occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class employer_total_co_greenwood_village_occupational_privilege_tax_employee_months(
    Variable
):
    value_type = int
    entity = Person
    label = "Employer Greenwood Village occupational privilege taxable employee-months"
    documentation = (
        "Annual count of taxable employee-months for Greenwood Village's "
        "employer occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class employer_total_co_greenwood_village_occupational_privilege_tax_owner_months(
    Variable
):
    value_type = int
    entity = Person
    label = "Employer Greenwood Village occupational privilege owner-months"
    documentation = (
        "Annual count of owner, partner, or officer months subject only to "
        "Greenwood Village's employer occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class employer_total_co_sheridan_occupational_privilege_tax_employee_months(Variable):
    value_type = int
    entity = Person
    label = "Employer Sheridan occupational privilege taxable employee-months"
    documentation = (
        "Annual count of taxable employee-months for Sheridan's employer "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class employer_total_mo_st_louis_payroll_expense(Variable):
    value_type = float
    entity = Person
    label = "Employer St. Louis payroll expense"
    documentation = (
        "Aggregate compensation subject to the St. Louis payroll expense tax."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_or_trimet_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer TriMet taxable wages"
    documentation = (
        "Aggregate wages for services performed within the TriMet district "
        "that are subject to the transit payroll tax."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_or_lane_transit_district_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer Lane Transit District taxable wages"
    documentation = (
        "Aggregate wages for services performed within the Lane Transit "
        "District that are subject to the transit payroll tax."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_wa_seattle_social_housing_excess_compensation(Variable):
    value_type = float
    entity = Person
    label = "Employer Seattle social housing excess compensation"
    documentation = (
        "Aggregate Seattle compensation above the Social Housing Tax's "
        "employee-level threshold."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_wa_seattle_payroll_expense_prior_year_total(Variable):
    value_type = float
    entity = Person
    label = "Employer Seattle payroll expense prior-year total payroll"
    documentation = (
        "Aggregate prior-year Seattle payroll expense used to determine "
        "whether the Seattle payroll expense tax applies."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_wa_seattle_payroll_expense_current_year_total(Variable):
    value_type = float
    entity = Person
    label = "Employer Seattle payroll expense current-year total payroll"
    documentation = (
        "Aggregate current-year Seattle payroll expense used to determine "
        "the Seattle payroll expense tax rate schedule."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_wa_seattle_payroll_expense_lower_band_taxable_payroll(Variable):
    value_type = float
    entity = Person
    label = "Employer Seattle payroll expense lower-band taxable payroll"
    documentation = (
        "Aggregate Seattle payroll expense subject to the lower taxable "
        "compensation band of the Seattle payroll expense tax."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class employer_total_wa_seattle_payroll_expense_upper_band_taxable_payroll(Variable):
    value_type = float
    entity = Person
    label = "Employer Seattle payroll expense upper-band taxable payroll"
    documentation = (
        "Aggregate Seattle payroll expense subject to the upper taxable "
        "compensation band of the Seattle payroll expense tax."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
