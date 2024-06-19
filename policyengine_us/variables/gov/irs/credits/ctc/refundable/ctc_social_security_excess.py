from policyengine_us.model_api import *


class ctc_social_security_excess(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable Child Tax Credit Social Security Excess"
    unit = USD
    documentation = (
        "The excess amount in social security for child tax credit calculation"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#d"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.ctc.refundable
        # Compute "Social Security taxes" as defined in the US Code for the ACTC.
        # This includes OASDI and Medicare payroll taxes, as well as half
        # of self-employment taxes.
        ss_add_variables = add(tax_unit, period, p.ss_add)
        ss_subtract_variables = add(tax_unit, period, p.ss_subtract)
        return ss_add_variables - ss_subtract_variables
