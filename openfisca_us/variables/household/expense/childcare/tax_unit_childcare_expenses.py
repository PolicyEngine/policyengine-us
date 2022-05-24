from openfisca_us.model_api import *


class tax_unit_childcare_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Distribute the childcare expenses evenly across the SPM unit's members.
        spmu = tax_unit.spm_unit
        spmu_childcare = spmu("childcare_expenses", period)
        spmu_size = spmu("spm_unit_size", period)
        tu_size = tax_unit("tax_unit_size", period)
        return spmu_childcare * (tu_size / spmu_size)
