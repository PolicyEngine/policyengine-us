"""Named OACT A9 mechanics; applying this preset opts into the contribution."""

from policyengine_core.reforms import Reform


class a9(Reform):
    def apply(self):
        # Shared systems call this unbound method with the system as self.
        self.modify_parameters(a9.configure_parameters)

    @staticmethod
    def configure_parameters(parameters):
        p = parameters.gov.contrib.ssa.benefit_levers.cola.means_test
        values = {
            "enabled": True,
            "scope": 1,
            "effective_year": 2028,
            "effective_month": 12,
            "below_threshold_cola_index": 1,
            "pre_receipt_cola_index": 1,
            "income_sensitivity": 0,
        }
        for name, value in values.items():
            getattr(p, name).update(start="0001-01-01", value=value)
        for name, value in {
            "base_year": 2018,
            "single": 85000,
            "joint": 170000,
            "index_lag": 1,
            "rounding": 100,
        }.items():
            getattr(p.thresholds, name).update(start="0001-01-01", value=value)
        for name, value in {
            "SINGLE": 0,
            "JOINT": 1,
            "SEPARATE": 0,
            "HEAD_OF_HOUSEHOLD": 0,
            "SURVIVING_SPOUSE": 1,
        }.items():
            getattr(p.filing_groups, name).update(start="0001-01-01", value=value)
        return parameters
