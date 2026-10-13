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
        # Social Services Law 209(2)(a)-(e), (2-a)
        "https://www.nysenate.gov/legislation/laws/SOS/209",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-3.2",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.4",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.otda.ssp
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
        couple = where(
            minor_enhanced_care,
            p.amount.couple.LIVING_WITH_OTHERS,
            p.amount.couple[arrangement] + 2 * premium,
        )
        payment = ssi_state_supplement(
            person,
            period,
            parameters,
            individual,
            couple,
            federal_payment_rules=False,
        )
        payment = where(payment > 0, max_(payment, p.minimum_payment), 0)
        federal = person("ssi_federal_living_arrangement", period)
        medical = federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        personal_needs_eligible = (
            medical
            & (person("ssi", period) > 0)
            & (person("ssi_countable_income", period) == 0)
        )
        personal_needs = select(
            [
                arrangement == la.NURSING_FACILITY,
                arrangement == la.OTHER_MEDICAL_FACILITY,
            ],
            [
                p.personal_needs.nursing_facility,
                p.personal_needs.other_medical_facility,
            ],
            default=0,
        )
        return payment + personal_needs_eligible * personal_needs
