from policyengine_us.model_api import *


class ok_federal_eitc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum federal EITC for the Oklahoma EITC computation"
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    unit = USD
    defined_for = StateCode.OK
    documentation = """
    Maximum federal EITC amount using FROZEN 2020 parameters.

    Oklahoma's EITC is based on federal EITC parameters frozen at 2020 levels.
    This variable returns the maximum credit amount based on the number of
    qualifying children, using 2020 federal values regardless of current year.

    2020 Maximum EITC by number of children:
    - 0 children: $538
    - 1 child: $3,584
    - 2 children: $5,920
    - 3+ children: $6,660

    Note: The parameters() call explicitly uses "2020-01-01" to ensure
    frozen parameter values are used regardless of the simulation period.
    """

    def formula(tax_unit, period, parameters):
        child_count = tax_unit("eitc_child_count", period)
        # Use FROZEN 2020 parameters per Oklahoma statute
        eitc = parameters("2020-01-01").gov.irs.credits.eitc
        return eitc.max.calc(child_count)
