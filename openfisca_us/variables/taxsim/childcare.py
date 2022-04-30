from openfisca_us.model_api import *
from ..irs.income.sources import tax_unit_childcare_expenses

childcare = variable_alias("childcare", tax_unit_childcare_expenses)