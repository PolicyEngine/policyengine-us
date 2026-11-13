from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ny_ssp(Variable):
    value_type = float
    entity = Person
    label = "New York State Supplement Program payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        # Social Services Law 209(2)(a)-(e), (2-a), (4)
        "https://www.nysenate.gov/legislation/laws/SOS/209",
        # 18 NYCRR 398-2.1(g), (l), (o), (ac)
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-2.1",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-3.2",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-3.4",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.2",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.4",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.otda.ssp
        fbr = parameters(period).gov.ssa.ssi.amount
        arrangement = person("ny_ssp_living_arrangement", period)
        la = arrangement.possible_values
        # A minor in level III receives the living-with-others rate.
        minor = person("ny_ssp_is_minor", period.this_year)
        minor_enhanced_care = minor & (arrangement == la.ENHANCED_RESIDENTIAL_CARE)
        county = person.household("county_str", period.this_year)
        downstate = np.isin(county, p.downstate_counties)
        premium = downstate * select(
            [arrangement == la.FAMILY_CARE, arrangement == la.RESIDENTIAL_CARE],
            [p.family_care_downstate_premium, p.residential_care_downstate_premium],
            default=0,
        )
        individual = where(
            minor_enhanced_care,
            p.amount.individual.LIVING_WITH_OTHERS,
            p.amount.individual[arrangement] + premium,
        )
        congregate_care = (
            (arrangement == la.FAMILY_CARE)
            | (arrangement == la.RESIDENTIAL_CARE)
            | (arrangement == la.ENHANCED_RESIDENTIAL_CARE)
        ) & ~minor_enhanced_care
        household_couple = select(
            [
                arrangement == la.LIVING_ALONE,
                (arrangement == la.LIVING_WITH_OTHERS) | minor_enhanced_care,
            ],
            [p.amount.couple.LIVING_ALONE, p.amount.couple.LIVING_WITH_OTHERS],
            default=0,
        )
        # Social Services Law 209(2)(c)-(e): a congregate care couple's standard
        # of need is two times the individual standard, so its supplement moves
        # with each federal benefit increase.
        couple = where(
            congregate_care,
            2 * (fbr.individual + individual) - fbr.couple,
            household_couple,
        )
        # NOTE: 18 NYCRR 398-2.1(l) requires both spouses to be in active
        # receipt of SSI. The federal couple computation ignores take-up, so a
        # couple in which an aged, blind or disabled spouse declines SSI is
        # still computed as a couple.
        payment = ssi_state_supplement(
            person,
            period,
            parameters,
            individual,
            couple,
            federal_payment_rules=False,
        )
        # NOTE: Under spousal deeming, New York's sources differ. The shared
        # helper follows SSA's method for federally administered supplements
        # (POMS SI 01320.430 D), which uses the couple rate. Social Services Law
        # 209(4) subtracts "the sum of such individual's or couple's
        # supplemental security income benefit plus countable income". 18 NYCRR
        # 398-2.1(ac) and 398-4.4(b) subtract "the FBR or a recipient's monthly
        # Countable Income, whichever is greater", where the FBR is "the maximum
        # amount of SSI payable to an individual or couple with no countable
        # income" (398-2.1(o)). New York administers its own supplement since
        # October 1, 2014, and the model follows the regulation: countable
        # income includes the deemed income (398-2.1(g)), measured against the
        # individual's own FBR.
        deeming = person("is_ssi_spousal_deeming_applies", period.this_year)
        federal_la = person("ssi_federal_living_arrangement", period)
        # 20 CFR 416.1131(a): one-third of the FBR counts as income in another
        # person's household.
        own_fbr = fbr.individual * where(
            federal_la == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            1 - fbr.one_third_reduction_rate,
            1,
        )
        countable = person("ssi_countable_income", period)
        regulatory = max_(individual - max_(countable - own_fbr, 0), 0)
        eligible = person("is_ssi_eligible", period) & person(
            "takes_up_ssi_if_eligible", period.this_year
        )
        payment = where(deeming, eligible * regulatory, payment)
        # Social Services Law 209(1)(d): no state payment in a public
        # institution or a medical facility where Medicaid pays more than half
        # the cost; only the personal needs allowance is paid there.
        no_standard = (
            (arrangement == la.NONE)
            | (arrangement == la.RESIDENTIAL_HEALTH_CARE_FACILITY)
            | (arrangement == la.DEVELOPMENTAL_OR_MENTAL_HEALTH_FACILITY)
        )
        payment = where(no_standard, 0, payment)
        payment = where(payment > 0, max_(payment, p.minimum_payment), 0)
        # NOTE: The 2026 OTDA chart gives $5 to residents of "other medical
        # facilities"; Social Services Law 209(2-a) and 18 NYCRR 398-3.4 limit
        # the $5 allowance to OPWDD intermediate care facilities and OMH
        # hospitals and pay $25 in residential health care facilities. The
        # model follows the statute and regulation.
        personal_needs_eligible = (person("ssi", period) > 0) & (
            person("ssi_countable_income", period) == 0
        )
        personal_needs = select(
            [
                arrangement == la.RESIDENTIAL_HEALTH_CARE_FACILITY,
                arrangement == la.DEVELOPMENTAL_OR_MENTAL_HEALTH_FACILITY,
            ],
            [
                p.personal_needs.residential_health_care_facility,
                p.personal_needs.developmental_or_mental_health_facility,
            ],
            default=0,
        )
        return payment + personal_needs_eligible * personal_needs
