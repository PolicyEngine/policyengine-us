from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.childcare.childcare_provider_type_group import (
    ChildcareProviderTypeGroup,
)


class COCCAPProviderType(Enum):
    LICENSED_CENTER = "Licensed child care center"
    LICENSED_HOME = "Licensed family child care home"
    QUALIFIED_EXEMPT = "Qualified exempt child care provider"


class co_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = COCCAPProviderType
    default_value = COCCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program provider type"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130(B), PDF page 119: rate types by provider type.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
        # 3.103(MMMM), PDF page 17: qualified exempt child care provider.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=17",
    )

    def formula(person, period, parameters):
        provider_type = person("childcare_provider_type_group", period.this_year)
        # Colorado pays license-exempt care only through qualified exempt
        # providers, so every license-exempt group takes the Exempt rates.
        return select(
            [
                provider_type == ChildcareProviderTypeGroup.DCC_SACC,
                provider_type == ChildcareProviderTypeGroup.FDC_GFDC,
            ],
            [
                COCCAPProviderType.LICENSED_CENTER,
                COCCAPProviderType.LICENSED_HOME,
            ],
            default=COCCAPProviderType.QUALIFIED_EXEMPT,
        )
