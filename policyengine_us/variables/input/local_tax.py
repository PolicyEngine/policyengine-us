from policyengine_us.model_api import *


class pa_philadelphia_wage_tax_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Philadelphia wage tax taxable wages"
    documentation = (
        "Compensation subject to Philadelphia's wage tax or employee earnings "
        "tax for this person."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class pa_philadelphia_wage_tax_resident(Variable):
    value_type = bool
    entity = Person
    label = "Philadelphia wage tax resident status"
    documentation = (
        "Whether this person is treated as a Philadelphia resident for wage "
        "tax purposes."
    )
    definition_period = YEAR
    default_value = False


class pa_philadelphia_wage_tax_reduced_rate_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Philadelphia reduced wage tax rate"
    documentation = (
        "Whether this person qualifies for Philadelphia's reduced 1.5% "
        "income-based wage tax rate."
    )
    definition_period = YEAR
    default_value = False


class mo_kansas_city_earnings_tax_taxable_earnings(Variable):
    value_type = float
    entity = Person
    label = "Kansas City earnings tax taxable earnings"
    documentation = "Earnings subject to Kansas City's 1% earnings tax for this person."
    unit = USD
    definition_period = YEAR
    default_value = 0


class mo_st_louis_earnings_tax_taxable_earnings(Variable):
    value_type = float
    entity = Person
    label = "St. Louis earnings tax taxable earnings"
    documentation = (
        "Earnings subject to the City of St. Louis earnings tax for this person."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class mo_st_louis_earnings_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "St. Louis earnings tax credit"
    documentation = (
        "Optional credit against St. Louis earnings tax, such as for taxes "
        "paid to another state or political subdivision."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0


class co_denver_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Denver employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Denver's employee "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class co_glendale_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Glendale employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Glendale's employee "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class co_greenwood_village_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Greenwood Village employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Greenwood Village's "
        "employee occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0


class co_sheridan_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Sheridan employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Sheridan's employee "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0
