# Validation against TAXSIM

PolicyEngine runs the same Enhanced CPS households through PolicyEngine US and through NBER's [TAXSIM](https://taxsim.nber.org/taxsim35/), and compares the federal and state income tax each one calculates. The comparison is maintained in [policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim). Its [dashboard](https://www.policyengine.org/us/taxsim/dashboard) has state-by-state results, side-by-side outputs for a sample of households, and the complete comparison data for each year.

## Results

The table below is loaded from the results the dashboard publishes, so it always matches the dashboard.

```{raw} html
<div id="taxsim-validation-results">
  <p>Loading the latest results from the <a href="https://www.policyengine.org/us/taxsim/dashboard">TAXSIM dashboard</a>…</p>
</div>
<noscript>
  <p>This table needs JavaScript. The same results are on the <a href="https://www.policyengine.org/us/taxsim/dashboard">TAXSIM dashboard</a>.</p>
</noscript>
<script>
(function () {
  "use strict";
  // Keep in sync with AVAILABLE_YEARS in policyengine-taxsim
  // dashboard/src/constants/index.js.
  var YEARS = [2021, 2022, 2023, 2024, 2025];
  var DATA_URL = "https://www.policyengine.org/us/taxsim/data/";
  var DASHBOARD_URL = "https://www.policyengine.org/us/taxsim/dashboard";
  var STATE_NAMES = {
    AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California",
    CO: "Colorado", CT: "Connecticut", DE: "Delaware", DC: "District of Columbia",
    FL: "Florida", GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois",
    IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana",
    ME: "Maine", MD: "Maryland", MA: "Massachusetts", MI: "Michigan",
    MN: "Minnesota", MS: "Mississippi", MO: "Missouri", MT: "Montana",
    NE: "Nebraska", NV: "Nevada", NH: "New Hampshire", NJ: "New Jersey",
    NM: "New Mexico", NY: "New York", NC: "North Carolina", ND: "North Dakota",
    OH: "Ohio", OK: "Oklahoma", OR: "Oregon", PA: "Pennsylvania",
    RI: "Rhode Island", SC: "South Carolina", SD: "South Dakota",
    TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont", VA: "Virginia",
    WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming"
  };
  var root = document.getElementById("taxsim-validation-results");

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      node.setAttribute(key, attrs[key]);
    });
    (children || []).forEach(function (child) {
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  function percent(value) {
    return typeof value === "number" && isFinite(value) && value >= 0 && value <= 100
      ? value
      : null;
  }

  // Returns null unless every field the table shows is present and valid.
  function parse(year, raw) {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
    var records = raw.totalRecords;
    if (typeof records !== "number" || records % 1 !== 0 || records <= 0) return null;
    var row = {
      year: year,
      records: records,
      federal1Pct: percent(raw.federalMatchPctRel),
      federal15: percent(raw.federalMatchPct),
      state1Pct: percent(raw.stateMatchPctRel),
      state15: percent(raw.stateMatchPct),
      // Summaries generated before the srebate column existed have no net metric.
      stateNet: raw.stateMatchPctRelNet === undefined ? null : percent(raw.stateMatchPctRelNet)
    };
    if (row.federal1Pct === null || row.federal15 === null || row.state1Pct === null || row.state15 === null) {
      return null;
    }
    if (raw.stateMatchPctRelNet !== undefined && row.stateNet === null) return null;
    var meta = raw.metadata && typeof raw.metadata === "object" ? raw.metadata : {};
    row.version = typeof meta.policyengineUsVersion === "string" ? meta.policyengineUsVersion : null;
    row.date = typeof meta.generatedAt === "string" ? meta.generatedAt.slice(0, 10) : null;
    // Mirrors the dashboard's notice that some states used an earlier TAXSIM build.
    var fb = meta.taxsimFallback;
    var states = fb && fb.appliesToThisYear === true ? (Array.isArray(fb.states) ? fb.states : [fb.state]) : [];
    row.fallbackStates = states.filter(function (s) {
      return typeof s === "string" && /^[A-Z]{2}$/.test(s);
    });
    return row;
  }

  function load(year) {
    return fetch(DATA_URL + year + "/summary_" + year + ".json")
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      })
      .then(function (raw) { return parse(year, raw); })
      .catch(function () { return null; });
  }

  function unique(values) {
    return values.filter(function (v, i) { return v !== null && values.indexOf(v) === i; });
  }

  function yearRange(years) {
    var contiguous = years.every(function (y, i) { return i === 0 || y === years[i - 1] + 1; });
    return contiguous && years.length > 1 ? years[0] + "–" + years[years.length - 1] : years.join(", ");
  }

  function listStates(codes) {
    var names = codes.map(function (c) { return STATE_NAMES[c] || c; });
    return names.length <= 2 ? names.join(" and ") : names.slice(0, -1).join(", ") + " and " + names[names.length - 1];
  }

  function pct(value) {
    return value === null ? "—" : value.toFixed(1) + "%";
  }

  function dashboardLink(text) {
    return el("a", { href: DASHBOARD_URL }, [text]);
  }

  function render(rows) {
    var results = rows.filter(function (r) { return r !== null; });
    var failed = YEARS.filter(function (y, i) { return rows[i] === null; });
    root.textContent = "";
    if (results.length === 0) {
      root.appendChild(el("p", {}, ["The latest results could not be loaded. They are on the ", dashboardLink("TAXSIM dashboard"), "."]));
      return;
    }
    var records = unique(results.map(function (r) { return r.records; }));
    var sameRecords = records.length === 1;
    var intro = "Share of records where the two models agree, for tax years " +
      yearRange(results.map(function (r) { return r.year; })) + ".";
    if (sameRecords) intro += " Each year compares " + records[0].toLocaleString("en-US") + " household records.";
    root.appendChild(el("p", {}, [intro]));

    var head1 = [el("th", { scope: "col", rowspan: "2", class: "head" }, ["Tax year"])];
    if (!sameRecords) head1.push(el("th", { scope: "col", rowspan: "2", class: "head" }, ["Records"]));
    head1.push(el("th", { scope: "colgroup", colspan: "2", class: "head" }, ["Federal income tax"]));
    head1.push(el("th", { scope: "colgroup", colspan: "3", class: "head" }, ["State income tax"]));
    var head2 = ["Within 1% of income", "Within $15", "Within 1% of income", "Within 1%, net of rebates", "Within $15"]
      .map(function (label) { return el("th", { scope: "col", class: "head" }, [label]); });
    var body = results.map(function (r) {
      var cells = [el("th", { scope: "row" }, [String(r.year)])];
      if (!sameRecords) cells.push(el("td", {}, [r.records.toLocaleString("en-US")]));
      [r.federal1Pct, r.federal15, r.state1Pct, r.stateNet, r.state15].forEach(function (v) {
        cells.push(el("td", {}, [pct(v)]));
      });
      return el("tr", {}, cells);
    });
    var table = el("table", {
      class: "docutils align-default taxsim-validation-table",
      "aria-label": "Share of records where PolicyEngine and TAXSIM agree, by tax year"
    }, [
      el("thead", {}, [el("tr", {}, head1), el("tr", {}, head2)]),
      el("tbody", {}, body)
    ]);
    root.appendChild(el("div", { class: "taxsim-validation-scroll" }, [table]));

    var versions = unique(results.map(function (r) { return r.version; }));
    var dates = unique(results.map(function (r) { return r.date; })).sort();
    var parts = [];
    if (versions.length) parts.push("policyengine-us " + versions.join(", "));
    if (dates.length) parts.push("generated " + (dates.length === 1 ? dates[0] : dates[0] + " to " + dates[dates.length - 1]));
    if (parts.length) root.appendChild(el("p", {}, ["Results computed with " + parts.join(", ") + "."]));

    var byStates = {};
    results.forEach(function (r) {
      if (!r.fallbackStates.length) return;
      var key = r.fallbackStates.join(",");
      (byStates[key] = byStates[key] || []).push(r.year);
    });
    Object.keys(byStates).forEach(function (key) {
      root.appendChild(el("p", {}, [
        "For " + yearRange(byStates[key]) + ", the TAXSIM results for " + listStates(key.split(",")) +
        " come from the previous TAXSIM build; other states use the updated build."
      ]));
    });
    if (failed.length) {
      root.appendChild(el("p", {}, ["Results for " + yearRange(failed) + " could not be loaded. The ", dashboardLink("dashboard"), " has every year."]));
    }
  }

  Promise.all(YEARS.map(load)).then(render);
})();
</script>
<style>
  .taxsim-validation-scroll { overflow-x: auto; margin-bottom: 1rem; }
  .taxsim-validation-table th.head { text-align: center; }
  .taxsim-validation-table td { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
</style>
```

## How agreement is measured

Each test compares PolicyEngine with TAXSIM for one record at a time, separately for federal income tax and state income tax. A cell in the table is the share of records that pass.

- **Within 1% of income** (the dashboard's default view): the two amounts differ by less than 1% of the record's gross income. Gross income here is wages, self-employment income, interest, dividends, other property income, non-property income, pensions and unemployment compensation, plus short- and long-term capital gains when positive and 85% of Social Security benefits. Records with zero or negative gross income use the \$15 test instead.
- **Within 1%, net of rebates** (state only): the same test applied to state income tax plus one-time state rebates on both sides. TAXSIM counts a rebate in the year it is paid and PolicyEngine in the tax year it relates to; netting rebates out removes that timing difference.
- **Within \$15**: the two amounts differ by \$15 or less.

These rules are implemented in `match_flags` in [`scripts/refresh_dashboard.py`](https://github.com/PolicyEngine/policyengine-taxsim/blob/main/scripts/refresh_dashboard.py), which produces the published results.
