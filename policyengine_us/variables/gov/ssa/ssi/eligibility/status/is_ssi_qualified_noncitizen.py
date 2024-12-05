from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person.immigration_status import (
    ImmigrationStatus,
)
import numpy as np


class is_ssi_qualified_noncitizen(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI qualified noncitizen"
    definition_period = YEAR

    def formula(person, period, parameters):
        status = person("immigration_status", period)
        qualifying_quarters_earnings = person(
            "ssi_qualifying_quarters_earnings", period
        )
        qualifying_quarters_threshold = parameters(
            period
        ).gov.ssa.ssi.income.sources.ssi_qualifying_quarters_threshold
        qualified_statuses = parameters(
            period
        ).gov.ssa.ssi.eligibility.status.qualified_noncitizen_status

        qualified_status_checks = []
        for qualified_status in qualified_statuses:
            # LPR's need 40 Qualifying Quarters of Earnings
            if qualified_status == "LEGAL_PERMANENT_RESIDENT":
                check = np.logical_and(
                    status == ImmigrationStatus.LEGAL_PERMANENT_RESIDENT,
                    qualifying_quarters_earnings
                    >= qualifying_quarters_threshold,
                )
            else:
                check = status == getattr(ImmigrationStatus, qualified_status)
            qualified_status_checks.append(check)

        return np.any(qualified_status_checks, axis=0)
