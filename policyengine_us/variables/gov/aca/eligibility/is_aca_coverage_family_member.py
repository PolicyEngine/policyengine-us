from policyengine_us.model_api import *


class is_aca_coverage_family_member(Variable):
    value_type = bool
    entity = Person
    label = "Member of the premium tax credit coverage family"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/26/1.36B-3#b_2",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-3#f_1",
    )
    documentation = (
        "A Marketplace enrollee (pays_aca_premium) who is in the premium tax "
        "credit tax family. 26 CFR 1.36B-3(b)(2) defines the coverage family "
        "as the members of the taxpayer's family for whom the month is a "
        "coverage month, and the benchmark plan in 1.36B-3(f) is the one "
        "offered to the coverage family. An enrollee who can be claimed on "
        "another return buys a plan but is not in it."
    )

    def formula(person, period, parameters):
        return person("pays_aca_premium", period) & person(
            "is_aca_tax_family_member", period
        )
