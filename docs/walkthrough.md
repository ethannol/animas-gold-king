# Five-minute walkthrough

_Rendered from the ledger by `scripts/80_render_docs.py`; do not edit `walkthrough.md`._

**The question (30 s).** In August 2015 the Gold King Mine release sent three million
gallons of acidic, metal-laden water down Cement Creek into the Animas. The plume passed
in days. The interesting question is whether anything changed afterwards once you adjust
for how much water was flowing, and whether you could tell a release from a treatment
plant that started two months later.

**The trap (45 s).** Sampling surged after the release: at the four reaches from Silverton
to Durango, 59.2 metal sampling events a year before, then
129 a year in the two years after the treatment plant
started, with River Watch's share falling from 76% to
36%. Pool everything and the level change in Cement Creek
dissolved zinc comes out at -40 percent, about double
the single-organisation estimate. Much of that is a change in who sampled,
with what limits, at what times of year. So the confirmatory series use one organisation,
Colorado River Watch, which sampled monthly with one method from 2005 to 2025:
475 events before, 479 after.

**The method (60 s).** Pre-registered and frozen before fitting. Stage one: log
concentration against log discharge with two seasonal harmonics, fitted on the pre-period
by censored maximum likelihood, giving flow-adjusted residuals. Stage two: an interrupted
time series on those residuals with a pre-period slope, a level change and a slope change
at the release, the plume window excluded, Newey-West intervals with a
12-observation bandwidth. Non-detects stay censored; substitution is a
labelled sensitivity. The headline is dissolved zinc in Cement Creek,
245 samples.

**The headline (60 s).** Level change -20 percent,
interval -38 to 3,
p = 0.08. By the frozen rule: "no detectable lasting change".
Now the part that matters: start the pre-period in 2010 and it is
-19 percent (-29 to
-7); in 2013, -23
percent. The long pre-period carries a rising trend, 3.0
percent a year, the legacy of the Sunnyside bulkheads, and the counterfactual extrapolates
it. Stop the post-period at the end of 2016 and the sign flips to
41 percent: the first year after
the release was higher, not lower. The 27-fit grid runs from
-26 to 46 percent.

**Attribution (60 s).** A change-point search that was never told the release date puts
its strongest split at 2010-03, -65
months before the release. On the series with 3 coding
artefacts removed, the strongest split is 2016-02:
6 months after the release and
4 months after the plant started. The upstream
control, above the Gold King source, looks like it fell -21
percent too, but that is three zero-valued "non-detects" doing the work; cleaned, it is
-11 percent. The difference-in-differences level
change is -24 percent with a differential downward slope
after 2015: relative to the control, Cement Creek stepped down and kept drifting down. Across 64 site-metal-fraction
cells, 0 survive false-discovery control.

**The sentence to leave with (15 s).** A decline of about a fifth in flow-adjusted zinc
over the decade after 2015 is plausible; it is not detectable against the longest
pre-period, it did not start at the release, it is partly a decline relative to the
upstream control, and nothing in these series separates the release from the treatment
plant that started two months later. The
value of the study is that every one of those dependencies is on the table, pre-registered,
and reproducible from the committed snapshot.
