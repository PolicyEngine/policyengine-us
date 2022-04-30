from openfisca_us.model_api import *
from ..irs.income.sources import short_term_capital_gains

stcg = variable_alias("stcg", short_term_capital_gains)