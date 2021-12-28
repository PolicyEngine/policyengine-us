from openfisca_us.model_api import *


class fcc_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = "Federal poverty ratio per FCC"
    documentation = "SPM unit's ratio of IRS gross income to their federal poverty guideline"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/47/54.400#f"
    unit = "ratio"

    def formula(spm_unit, period, parameters):
        income = spm_unit.sum(spm_unit.members("irs_gross_income", period))
        fpg = spm_unit("spm_unit_fpg", period)
        return income / fpg
