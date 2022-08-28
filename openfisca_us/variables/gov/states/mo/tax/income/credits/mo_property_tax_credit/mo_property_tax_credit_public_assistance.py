from openfisca_us.model_api import *


class mo_property_tax_credit_public_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit demographic eligiblity test"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    reference2 = "https://dor.mo.gov/forms/4711_2021.pdf"
    leg_ref = "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        #"public assistance, SSI, child support, or Temporary Assistance payments (TA and TANF)"
        #the second reference specifies that food stamps are not counted as income for this form. 
        person = spm_unit.members
        fully_disabled_service_connected_veteran = person("is_fully_disabled_service_connected_veteran", period)
        spm_unit = tax_unit.spm_unit
        tanf = spm_unit("tanf", period)
        ssi = spm_unit("ssi", period)
        pension = person("pension_income", period)
        benefits_sum = tanf + ssi + pension
        return where(fully_disabled_service_connected_veteran == 1, 0, benefits_sum)