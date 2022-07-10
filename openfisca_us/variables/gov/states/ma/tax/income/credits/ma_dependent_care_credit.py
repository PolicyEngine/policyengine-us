from openfisca_us.model_api import *
from openfisca_us.variables.gov.irs.credits.cdcc.count_cdcc_eligible import (
    count_cdcc_eligible,
)


class ma_dependent_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6"  # (y)
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.credits.dependent_care
        count_cdcc_eligible = tax_unit("count_cdcc_eligible", period)
        return p.amount.calc(count_cdcc_eligible)
