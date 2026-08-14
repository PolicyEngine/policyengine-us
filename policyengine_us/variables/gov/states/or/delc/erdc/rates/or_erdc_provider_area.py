from policyengine_us.model_api import *


class ORERDCProviderArea(Enum):
    AREA_A = "Area A"
    AREA_B = "Area B"
    AREA_C = "Area C"


class or_erdc_provider_area(Variable):
    value_type = Enum
    entity = Person
    possible_values = ORERDCProviderArea
    # We don't track a family's provider location at the moment, so this
    # defaults to Area C. Areas B and C share an identical rate schedule, so the
    # default is exact for those families but understates rates for Area A
    # (metro ZIP) families, whose rates are higher. In population runs that
    # understatement partly offsets the upward bias from the highest-rate
    # CERTIFIED_CENTER provider-type default. The remedy is populating provider
    # area from data or overriding it as an input, not changing this default.
    default_value = ORERDCProviderArea.AREA_C
    definition_period = MONTH
    label = "Oregon ERDC provider rate area"
    defined_for = StateCode.OR
    reference = "https://www.oregon.gov/delc/programs/pages/rates.aspx"
