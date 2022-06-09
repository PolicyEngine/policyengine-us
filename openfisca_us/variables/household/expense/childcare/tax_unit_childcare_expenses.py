from openfisca_us.model_api import *


class tax_unit_childcare_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Distribute the childcare expenses evenly across the SPM unit's members.
        spm_unit = tax_unit.spm_unit
        spm_unit_childcare = spm_unit("childcare_expenses", period)
        spm_unit_size = spm_unit("spm_unit_size", period)
        tax_unit_size = tax_unit("tax_unit_size", period)
        return spm_unit_childcare * (tax_unit_size / spm_unit_size)
