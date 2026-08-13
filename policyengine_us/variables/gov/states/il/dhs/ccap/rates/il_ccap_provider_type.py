from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.childcare.childcare_provider_type_group import (
    ChildcareProviderTypeGroup,
)


class ILCCAPProviderType(Enum):
    LICENSED_CENTER = "Licensed center"
    LICENSE_EXEMPT_CENTER = "License-exempt center"
    LICENSED_HOME = "Licensed home or group home"
    LICENSE_EXEMPT_HOME = "License-exempt home or in-home care"


class il_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = ILCCAPProviderType
    default_value = ILCCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Illinois CCAP provider type"
    defined_for = StateCode.IL
    # Center provider types 760 and 761 are on page 1 of the rate schedule; the
    # home provider types 762 through 767 continue on page 2.
    reference = "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/pages/ccap-for-providers/IL444-4343%20-%20Child%20Care%20Payment%20Rates%20for%20Child%20Care%20Providers%207.1.26.pdf#page=1"

    def formula(person, period, parameters):
        provider_type = person(
            "childcare_provider_type_group",
            period.this_year,
        )
        return select(
            [
                provider_type == ChildcareProviderTypeGroup.DCC_SACC,
                provider_type == ChildcareProviderTypeGroup.LE_GC,
                provider_type == ChildcareProviderTypeGroup.FDC_GFDC,
                provider_type == ChildcareProviderTypeGroup.LE_STD,
                provider_type == ChildcareProviderTypeGroup.LE_ENH,
            ],
            [
                ILCCAPProviderType.LICENSED_CENTER,
                ILCCAPProviderType.LICENSE_EXEMPT_CENTER,
                ILCCAPProviderType.LICENSED_HOME,
                ILCCAPProviderType.LICENSE_EXEMPT_HOME,
                ILCCAPProviderType.LICENSE_EXEMPT_HOME,
            ],
            default=ILCCAPProviderType.LICENSED_CENTER,
        )
