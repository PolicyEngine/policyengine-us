from policyengine_us.model_api import *


class estate_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "Estate tax credit"
    unit = USD
    documentation = (
        "Unified credit against the estate tax under IRC § 2010(a). Under "
        "§ 2010(c)(1) the applicable credit amount is the tentative tax that "
        "§ 2001(c) would impose on the applicable exclusion amount, not the "
        "exclusion amount itself. Only the basic exclusion amount is used; "
        "the deceased spousal unused exclusion (DSUE) amount of § 2010(c)(4) "
        "is not yet modeled."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2010#c_1",
        "https://www.law.cornell.edu/uscode/text/26/2001#c",
    )
    defined_for = "is_deceased"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs
        # TODO: add the deceased spousal unused exclusion (DSUE) amount to the
        # basic exclusion amount to form the applicable exclusion amount
        # (IRC § 2010(c)(2)).
        applicable_exclusion_amount = np.full(person.count, p.credits.estate.base)
        return p.tax.estate.rate.calc(applicable_exclusion_amount)
