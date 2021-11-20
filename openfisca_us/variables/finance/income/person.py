from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class market_income(Variable):
    value_type = float
    entity = Person
    label = "Market income"
    unit = "currency-USD"
    documentation = "Income from non-benefit sources"
    definition_period = YEAR


class gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income"
    unit = "currency-USD"
    documentation = "Combined market and benefit income"
    definition_period = YEAR


class tax(Variable):
    value_type = float
    entity = Person
    label = "Tax"
    unit = "currency-USD"
    documentation = "Total tax liability"
    definition_period = YEAR


class benefits(Variable):
    value_type = float
    entity = Person
    label = "Benefits"
    unit = "currency-USD"
    documentation = "Total benefit entitlement"
    definition_period = YEAR


class net_income(Variable):
    value_type = float
    entity = Person
    label = "Net income"
    unit = "currency-USD"
    documentation = "Disposable income after taxes and transfers"
    definition_period = YEAR
