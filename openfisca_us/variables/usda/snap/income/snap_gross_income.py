from openfisca_us.model_api import *


class snap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SNAP gross income"
    documentation = "Gross income for calculating SNAP eligibility"
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#d"
    unit = USD

    def formula(spm_unit, period):
        return spm_unit.sum(spm_unit.members("market_income", period))
