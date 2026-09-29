from policyengine_us.model_api import *


class snap_alien_qualifying_quarters(Variable):
    value_type = int
    entity = Person
    label = "Qualifying quarters credited to an alien for the SNAP waiting period"
    documentation = (
        "Total qualifying quarters of work credited to the person under 8 USC "
        "1645 and 7 CFR 273.4(a)(6)(ii)(A), including quarters of work not "
        "covered by Title II of the Social Security Act. The total is the sum "
        "of the quarters the person worked, the quarters a parent worked "
        "before the person turned 18 (including quarters before the person "
        "was born or adopted), and the quarters a spouse worked during the "
        "marriage if the couple is still married or the spouse is deceased. "
        "A spouse's quarters do not count if the couple divorced before the "
        "SNAP eligibility determination (273.4(a)(6)(ii)(A)(1)). Enter the "
        "total net of quarters after December 31, 1996, in which the person, "
        "parent or spouse actually received any Federal means-tested public "
        "benefit or SNAP benefits, which are not creditable "
        "(273.4(a)(6)(ii)(A)(2)). Consulted only for lawful permanent "
        "residents inside the SNAP qualified alien waiting period. Defaults "
        "to 0, so the 40-quarter exception applies only when this input is "
        "supplied. This is the same legal count as "
        "ssi_qualifying_quarters_earnings. 8 USC 1612(a)(2)(B) is one "
        "exception, which 1612(a)(3) applies to both SSI and SNAP. 8 USC "
        "1645 sets one crediting rule for both programs. When both inputs "
        "are supplied for a person, they should hold the same number. The "
        "SNAP input is separate only because of the defaults: "
        "ssi_qualifying_quarters_earnings defaults to 40, so reusing it would "
        "exempt every lawful permanent resident and the waiting period would "
        "never apply."
    )
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1612#a_2_B",
        "https://www.law.cornell.edu/uscode/text/8/1612#a_3",
        "https://www.law.cornell.edu/uscode/text/8/1645",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_ii_A",
    )
