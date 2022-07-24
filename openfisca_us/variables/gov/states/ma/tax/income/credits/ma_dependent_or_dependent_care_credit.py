from openfisca_us.model_api import *


class ma_dependent_or_dependent_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA dependent or dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6"  # (x-y)
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # MA taxpayers can only take either the dependent credit or the
        # dependent care credit.
        return max_(
            tax_unit("ma_dependent_credit", period),
            tax_unit("ma_dependent_care_credit", period),
        )
