from policyengine_us.model_api import *
import numpy as np
import pandas as pd
from policyengine_us.parameters.gov.states.fl.doe.sr.rates.reimbursement import (
    get_reimbursement_rates,
)


class fl_sr_max_daily_rate(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Florida School Readiness maximum daily reimbursement rate"
    defined_for = StateCode.FL
    reference = "https://www.flrules.org/gateway/RuleNo.asp?id=6M-4.500"

    def formula(person, period, parameters):
        # Daily provider reimbursement rate looked up from the statewide
        # FY2025-26 schedule by county x provider type x care level x unit of
        # care (6M-4.500; SPB 2502). Vectorized via a left merge on the
        # enum member-name strings, mirroring the Texas CCS CSV-rate pattern.
        rates = get_reimbursement_rates(period.start.year)
        county = person.household("county_str", period.this_year)
        provider_type = person("fl_sr_provider_type", period)
        care_level = person("fl_sr_care_level", period)
        unit = person("fl_sr_time_category", period)
        lookup = pd.DataFrame(
            {
                "county": county,
                "provider_type": provider_type.decode_to_str(),
                "care_level": care_level.decode_to_str(),
                "unit": unit.decode_to_str(),
            }
        )
        lookup["_idx"] = np.arange(len(lookup))
        merged = lookup.merge(
            rates,
            how="left",
            on=["county", "provider_type", "care_level", "unit"],
        ).sort_values("_idx")
        # A county with no published rate (e.g. an unset county_str) yields 0
        # here; the benefit formula treats a zero cap as "uncapped" so a missing
        # county does not zero out the subsidy.
        return merged["rate"].fillna(0.0).values
