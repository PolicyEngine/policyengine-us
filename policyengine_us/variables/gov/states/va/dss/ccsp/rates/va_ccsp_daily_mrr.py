from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.va.dss.ccsp.rates.va_ccsp_provider_type import (
    VACCSPProviderType,
)


class va_ccsp_daily_mrr(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Virginia CCSP daily maximum reimbursable rate"
    defined_for = StateCode.VA
    reference = "https://data.virginia.gov/dataset/general-child-care-subsidy-program-maximum-reimbursement-rates"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dss.ccsp.maximum_reimbursement_rate
        region = person.household("va_ccsp_ready_region", period.this_year)
        provider_type = person("va_ccsp_provider_type", period.this_year)
        age_group = person("va_ccsp_care_age_group", period.this_year)
        is_full_day = person("va_ccsp_is_full_day", period.this_year)

        is_center = provider_type == provider_type.possible_values.CENTER
        center_rate = p.center[region][age_group]
        # Per the VDOE FY 2024 MRR table, FDH rates vary by Ready Region only;
        # within each region every age-group column carries the same rate, so
        # the FDH parameter is indexed by region alone (no age_group lookup).
        fdh_rate = p.family_day_home[region]
        full_day_rate = where(is_center, center_rate, fdh_rate)
        return where(is_full_day, full_day_rate, full_day_rate * p.part_day_factor)
