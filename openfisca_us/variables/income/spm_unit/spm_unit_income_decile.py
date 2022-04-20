from openfisca_us.model_api import *


class spm_unit_income_decile(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income decile"
    unit = int
    documentation = "The income decile of the SPM unit, using OECD-equivalised net income"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        from microdf import MicroSeries
        income = spm_unit("spm_unit_oecd_equiv_net_income", period)
        weights = spm_unit("spm_unit_weight", period)
        return MicroSeries(income, weights=weights).decile_rank()