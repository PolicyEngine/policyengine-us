from openfisca_us.model_api import *
from openfisca_us.variables.irs.income.sources import taxable_interest

intrec = variable_alias("intrec", taxable_interest)