from openfisca_us.model_api import *


class wic(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SPM unit's average benefit value for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "WIC benefit value"
    reference = "https://fns-prod.azureedge.net/sites/default/files/resource-files/WICPC2018FoodPackage-Summary.pdf#page=2"

    def formula(spm_unit, period, parameters):
        return aggr(spm_unit, period, ["wic_value"])
