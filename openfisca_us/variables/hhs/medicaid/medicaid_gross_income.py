from openfisca_us.model_api import *


class medicaid_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Medicaid gross income"
    documentation = "Gross income for calculating Medicaid eligibility"
    unit = USD

    def formula(spm_unit, period):
        return spm_unit.sum(spm_unit.members("market_income", period))
