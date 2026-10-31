from policyengine_us.model_api import *


class wa_pte_categorical_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Categorically eligible for the Washington Senior Citizens and Disabled Persons Property Tax Exemption"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-130",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.dor.property_tax_exemption.senior_disabled
        # RCW 84.36.381(3)(a)(i): at or above the age threshold, or retired
        # from regular gainful employment by reason of disability at the time
        # of filing. Generic disability establishes neither.
        senior = person("age", period) >= p.age_threshold
        retired_due_to_disability = person("wa_pte_retired_due_to_disability", period)
        # RCW 84.36.381(3)(a)(ii): a veteran entitled to and receiving VA
        # compensation at a combined service-connected evaluation rating of at
        # least the threshold, or at a total disability rating for a
        # service-connected disability. A 100 percent evaluation is a total
        # rating (38 CFR 3.340(a)(2)).
        veteran = person("is_veteran", period)
        compensated = person("wa_pte_receives_va_disability_compensation", period)
        rating = person("wa_pte_va_service_connected_rating", period)
        total_rating = person("wa_pte_va_total_disability_rating", period) | (
            rating >= 1
        )
        qualifying_rating = total_rating | (
            rating >= p.veteran.combined_rating_threshold
        )
        rated_veteran = compensated & qualifying_rating
        # Before collection year 2016 the veteran pathway was "one hundred
        # percent service-connected disability as provided in 42 U.S.C. Sec.
        # 423(d)(1)(A)", which can be read as a 100 percent VA rating or as a
        # wholly service-connected disability meeting the Social Security
        # definition; is_disabled stands in for it in those years.
        earlier_veteran = person("is_disabled", period)
        veteran_pathway = veteran & where(
            p.veteran.rating_requirement_in_effect, rated_veteran, earlier_veteran
        )
        return senior | retired_due_to_disability | veteran_pathway
