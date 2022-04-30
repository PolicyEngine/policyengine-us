from openfisca_us.model_api import *
from ..irs.income.sources import pension_income

pensions = variable_alias("pensions", pension_income)