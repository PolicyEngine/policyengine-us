from policyengine_us.model_api import *
from policyengine_us.reforms.utils import create_reform_threshold_check
import operator
import numpy as np


def create_increase_taxable_earnings_for_social_security() -> Reform:
    class taxable_earnings_for_social_security(Variable):
        value_type = float
        entity = Person
        label = "Taxable gross earnings for OASDI FICA"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            earnings = person("payroll_tax_gross_wages", period)
            p = parameters(period).gov
            base_taxable = min_(earnings, p.irs.payroll.social_security.cap)
            secondary_taxable = max_(
                0,
                earnings - p.contrib.cbo.payroll.secondary_earnings_threshold,
            )
            return base_taxable + secondary_taxable

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_earnings_for_social_security)

    return reform


def create_increase_taxable_earnings_for_social_security_reform(
    parameters, period, bypass: bool = False
):
    return create_reform_threshold_check(
        reform_function=create_increase_taxable_earnings_for_social_security,
        parameters=parameters,
        period=period,
        parameter_path="gov.contrib.cbo.payroll",
        comparison_parameter_path="secondary_earnings_threshold",
        comparison_operator=operator.lt,
        threshold_check=np.inf,
        bypass=bypass,
    )


increase_taxable_earnings_for_social_security = (
    create_increase_taxable_earnings_for_social_security_reform(
        None, None, bypass=True
    )
)
