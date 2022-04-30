from openfisca_us.model_api import *
from ..irs.income.sources import filer_partnership_s_corp_income

scorp = variable_alias("scorp", filer_partnership_s_corp_income)

