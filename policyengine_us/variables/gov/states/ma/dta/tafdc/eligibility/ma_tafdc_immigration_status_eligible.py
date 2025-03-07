from policyengine_us.model_api import *


class ma_tafdc_immigration_status_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to immigration status"
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/report-on-transitional-aid-to-families-with-dependent-children-eligible-noncitizen-status-1/download"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        immigration_status = tax_unit.members("immigration_status", period)
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        return tax_unit.any(~undocumented)
