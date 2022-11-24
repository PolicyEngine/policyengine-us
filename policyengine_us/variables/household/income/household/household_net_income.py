from policyengine_us.model_api import *
from microdf import MicroSeries

class household_net_income(Variable):
    value_type = float
    entity = Household
    label = "net income"
    definition_period = YEAR
    unit = USD
    adds = [
        "household_market_income",
        "household_benefits",
    ]
    subtracts = [
        "household_tax",
    ]

class equiv_household_net_income(Variable):
    value_type = float
    entity = Household
    label = "equivalised net income"
    definition_period = YEAR
    unit = USD
    adds = [
        "spm_unit_oecd_equiv_net_income",
    ]

class household_market_income(Variable):
    value_type = float
    entity = Household
    label = "market income"
    definition_period = YEAR
    unit = USD
    adds = [
        "spm_unit_market_income",
    ]

class household_tax(Variable):
    value_type = float
    entity = Household
    label = "tax"
    unit = USD
    definition_period = YEAR
    adds = [
        "spm_unit_taxes",
    ]

class household_benefits(Variable):
    value_type = float
    entity = Household
    label = "benefits"
    unit = USD
    definition_period = YEAR
    adds = [
        "spm_unit_benefits",
    ]

class household_income_decile(Variable):
    label = "household income decile"
    documentation = "Decile of household income (person-weighted)"
    entity = Household
    definition_period = YEAR
    value_type = int

    def formula(household, period, parameters):
        income = household("household_net_income", period)
        count_people = household("household_count_people", period)
        household_weight = household("household_weight", period)
        weighted_income = MicroSeries(income, weights=household_weight * count_people)
        return weighted_income.decile_rank().values

class in_poverty(Variable):
    label = "in poverty"
    documentation = "Whether household is in poverty"
    entity = Household
    definition_period = YEAR
    value_type = bool
    adds = [
        "spm_unit_is_in_spm_poverty",
    ]

class person_in_poverty(Variable):
    label = "person in poverty"
    documentation = "Whether person is in poverty"
    entity = Person
    definition_period = YEAR
    value_type = bool
    
    def formula(person, period, parameters):
        return person.household("in_poverty", period)

class poverty_gap(Variable):
    label = "poverty gap"
    documentation = "Poverty gap"
    entity = Household
    definition_period = YEAR
    value_type = float
    unit = USD

class income_decile(Variable):
    label = "income decile"
    documentation = "Decile of household net income. Households are sorted by disposable income, and then divided into 10 equally-populated groups."
    entity = Person
    definition_period = YEAR
    value_type = int

    def formula(person, period, parameters):
        return person.household("household_income_decile", period)

class household_count_people(Variable):
    value_type = int
    entity = Household
    label = "Number of people"
    definition_period = YEAR
    unit = "person"

    def formula(household, period, parameters):
        return household.nb_persons()