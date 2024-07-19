from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person.immigration_status import ImmigrationStatus
import numpy as np

class is_ssi_qualified_noncitizen(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI qualified noncitizen"
    definition_period = YEAR

    def formula(person, period, parameters):
        status = person("immigration_status", period)
        has_40qq_earnings = person("ssi_40qq_earnings", period)
        
        # Get the list of qualified noncitizen statuses to look for from parameters
        qualified_statuses = parameters(period).gov.ssa.ssi.eligibility.status.qualified_noncitizen

        # Create list of tests against immigration status
        conditions = []
        for qualified_status in qualified_statuses:
            if qualified_status == "LEGAL_PERMANENT_RESIDENT":
                # LPR's need 40 Qualifying Quarters of Earnings
                conditions.append(np.logical_and(status == ImmigrationStatus.LEGAL_PERMANENT_RESIDENT, has_40qq_earnings))
            else:
                conditions.append(status == getattr(ImmigrationStatus, qualified_status))

        # If any of the tests pass, return True
        qualified = np.select(
            conditions,
            [True] * len(conditions),
            default=False
        )
        return qualified