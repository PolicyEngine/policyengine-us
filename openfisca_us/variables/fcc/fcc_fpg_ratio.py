from openfisca_us.model_api import *


class fcc_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's federal poverty ratio as defined by the FCC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/47/54.400#f"

    def formula(spm_unit, period, parameters):
        income = spm_unit.sum(spm_unit.members("irs_gross_income", period))
        fpg = spm_unit("spm_unit_fpg", period)
        return income / fpg
