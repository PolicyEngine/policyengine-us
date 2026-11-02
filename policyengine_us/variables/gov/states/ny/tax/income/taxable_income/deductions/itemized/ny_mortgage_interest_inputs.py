from policyengine_us.model_api import *

_FAIR_MARKET_VALUE_DEFAULT = (
    "Leave at 0 if unknown. New York then counts the home as worth at least "
    "the debt on it, so only the $100,000 ($50,000 separate) home equity debt "
    "limit applies, as in PolicyEngine's Hawaii calculation."
)

_NON_ACQUISITION_DEBT_DEFAULT = (
    "Include the interest on this debt in the home mortgage interest inputs. "
    "PolicyEngine's federal calculation reads only the acquisition mortgage "
    "balances, so it does not disallow that interest federally after 2017. "
    "Defaults to 0, which leaves New York's calculation to the acquisition "
    "mortgage balances."
)


class ny_first_home_fair_market_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York first home fair market value"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.NY
    documentation = (
        "Fair market value of the main home, which limits the home equity "
        "debt New York allows on it under pre-TCJA IRC 163(h)(3)(C)(i). "
        + _FAIR_MARKET_VALUE_DEFAULT
    )
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"


class ny_second_home_fair_market_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York second home fair market value"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.NY
    documentation = (
        "Fair market value of the second home, which limits the home equity "
        "debt New York allows on it under pre-TCJA IRC 163(h)(3)(C)(i). "
        + _FAIR_MARKET_VALUE_DEFAULT
    )
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"


class ny_first_home_non_acquisition_debt(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York first home non-acquisition debt"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.NY
    documentation = (
        "Average balance of debt secured by the main home that is not home "
        "acquisition debt (not used to buy, build or substantially improve "
        "it), such as a home equity loan spent on other things. Pre-TCJA IRC "
        "163(h)(3)(C) treats it as home equity debt for New York. "
        + _NON_ACQUISITION_DEBT_DEFAULT
    )
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"


class ny_second_home_non_acquisition_debt(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York second home non-acquisition debt"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.NY
    documentation = (
        "Average balance of debt secured by the second home that is not home "
        "acquisition debt (not used to buy, build or substantially improve "
        "it). Pre-TCJA IRC 163(h)(3)(C) treats it as home equity debt for "
        "New York. " + _NON_ACQUISITION_DEBT_DEFAULT
    )
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"
