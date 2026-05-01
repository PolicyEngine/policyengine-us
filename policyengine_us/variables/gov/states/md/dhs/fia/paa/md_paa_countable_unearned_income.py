from policyengine_us.model_api import *


class md_paa_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20500%20Financial%20Eligibility%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-08",
    )

    def formula(person, period, parameters):
        # PAA Manual §500.8 / §500.11 / AT 23-02: federally funded
        # assistance, Social Security, and SSI/RSDI-type benefits all count
        # as unearned income for PAA, with a $20 disregard. We add `ssi`
        # explicitly because the federal `ssi_unearned_income` source list
        # does not include the SSI cash payment itself. The following PAA
        # countable-income refinements are not tracked at the moment and
        # should be treated as residual modeling gaps:
        #   - Lump sums (§500.7) and infrequent / irregular income (§500.9).
        #   - Parent / adult-child financial contributions (§500.8).
        #   - "Actually available" first-month income treatment (§500.8.A.5).
        #   - State-funded assistance categories outside the federal SSI
        #     source list.
        p = parameters(period).gov.states.md.dhs.fia.paa.income
        unearned = add(
            person,
            period,
            [
                "ssi",
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
        return max_(unearned - p.unearned_income_disregard, 0)
