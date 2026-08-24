=== Prompt V1 (baseline, no guidance) — Accuracy: 80.0% (12/15) ===
  [correct] expected=negative got=negative | Oh great, another update that breaks everything. Just perfect.
  [correct] expected=neutral  got=neutral  | The food was amazing but the service was painfully slow.
  [correct] expected=neutral  got=neutral  | I guess it's okay.
  [correct] expected=negative got=negative | Sure, take your time, it's not like I'm in a hurry or anything.
  [WRONG  ] expected=neutral  got=positive | It works.
  [correct] expected=positive got=positive | Best decision I've made all year, no regrets at all.
  [WRONG  ] expected=negative got=neutral  | Not the worst thing I've bought, but I wouldn't buy it again.
  [correct] expected=negative got=negative | Wow, five stars, truly a masterpiece of poor design.
  [correct] expected=positive got=positive | The room was clean, check-in was quick, staff were polite.
  [correct] expected=negative got=negative | Honestly? Kind of a letdown after all the hype.
  [correct] expected=neutral  got=neutral  | It does exactly what it says on the box, nothing more.
  [correct] expected=positive got=positive | I laughed, I cried, I'd do it all over again.
  [correct] expected=neutral  got=neutral  | The battery life is decent, the camera is mediocre, overall it's fine.
  [WRONG  ] expected=neutral  got=positive | Can't complain, does the job.
  [correct] expected=positive got=positive | Absolutely thrilled — this exceeded every expectation I had.

=== Prompt V2 (improved, handles sarcasm/mixed/flat cases) — Accuracy: 93.3% (14/15) ===
  [correct] expected=negative got=negative | Oh great, another update that breaks everything. Just perfect.
  [correct] expected=neutral  got=neutral  | The food was amazing but the service was painfully slow.
  [correct] expected=neutral  got=neutral  | I guess it's okay.
  [correct] expected=negative got=negative | Sure, take your time, it's not like I'm in a hurry or anything.
  [correct] expected=neutral  got=neutral  | It works.
  [correct] expected=positive got=positive | Best decision I've made all year, no regrets at all.
  [WRONG  ] expected=negative got=neutral  | Not the worst thing I've bought, but I wouldn't buy it again.
  [correct] expected=negative got=negative | Wow, five stars, truly a masterpiece of poor design.
  [correct] expected=positive got=positive | The room was clean, check-in was quick, staff were polite.
  [correct] expected=negative got=negative | Honestly? Kind of a letdown after all the hype.
  [correct] expected=neutral  got=neutral  | It does exactly what it says on the box, nothing more.
  [correct] expected=positive got=positive | I laughed, I cried, I'd do it all over again.
  [correct] expected=neutral  got=neutral  | The battery life is decent, the camera is mediocre, overall it's fine.
  [correct] expected=neutral  got=neutral  | Can't complain, does the job.
  [correct] expected=positive got=positive | Absolutely thrilled — this exceeded every expectation I had.

=== IMPROVEMENT ===
V1: 80.0%  ->  V2: 93.3%  (change: +13.3 points)

=== CASES THAT IMPROVED (wrong in V1, correct in V2) ===
  "It works."
    V1 said: positive (wrong)  ->  V2 said: neutral (correct, expected: neutral)
  "Can't complain, does the job."
    V1 said: positive (wrong)  ->  V2 said: neutral (correct, expected: neutral)
