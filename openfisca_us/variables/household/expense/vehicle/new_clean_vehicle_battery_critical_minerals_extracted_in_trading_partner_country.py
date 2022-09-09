from openfisca_us.model_api import *


class new_clean_vehicle_battery_critical_minerals_extracted_in_trading_partner_country(
    Variable
):
    value_type = float
    entity = TaxUnit
    label = "Percent of new clean vehicle's battery critical minerals extracted in a US trading partner country"
    documentation = "Percent of newly purchased new clean vehicle's battery critical minearls (by value) extracted or processed in any country with which the US has a free trade agreement in effect, or recycled in North America"
    unit = "/1"
    definition_period = YEAR
