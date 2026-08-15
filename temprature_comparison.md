# Temperature Comparison — Week 01 Task 04

**Prompt used:** "Write one sentence describing a sunset."

## Results Table

| Temperature | Run 1 | Run 2 | Run 3 | Variance observed |
|---|---|---|---|---|
| 0.0 | The sky bled brilliant shades of amber and violet as the sun slowly melted beneath the jagged silhouette of the horizon. | The sun melted into the horizon, bruising the evening sky with vibrant strokes of amber and violet. | As the sun dipped below the horizon, it painted the sky in brilliant strokes of fiery orange and deep violet, casting a warm, fading glow over the quiet earth. | Lowest variance of the three settings — all three share very similar vocabulary and structure ("melted," "amber," "violet," "horizon"), though not word-for-word identical. |
| 0.7 | The setting sun painted the horizon in bruised shades of violet and burning amber, slowly melting into the encroaching velvet of night. | The horizon blazed in a brilliant gradient of bruised violet and liquid gold as the sun slowly dipped below the edge of the world. | The horizon bled vibrant strokes of bruised purple and molten gold as the sun dipped lazily below the edge of the world. | Moderate variance — sentence structure and some phrases repeat ("bruised," "horizon," "dipped"), but color choices and verbs shift between runs. |
| 1.0 | The dying sun bled vibrant strokes of crimson and gold across the darkening canvas of the evening sky. | As the day melted away, the sky burst into brilliant shades of bruised purple and molten gold, slowly fading into the quiet embrace of twilight. | The sky bled molten gold and bruised violet as the sun slowly slipped beneath the jagged silhouette of the horizon. | Highest variance in structure and imagery (different opening clauses, different color pairings), though vocabulary still overlaps with the other two settings. |

## Analysis

Across all three temperature settings, the outputs used a similar poetic vocabulary bank — words like "bled," "bruised," "molten," and "horizon" appeared repeatedly regardless of temperature. This suggests the model has a strong learned association between "sunset" and this particular descriptive style, which persisted even at higher randomness settings. That said, a clear trend was still visible: at temperature 0.0, the three outputs were the most similar in structure and word choice, since lower temperature narrows the model toward its highest-probability phrasing rather than fully collapsing to one exact sentence. At 0.7, sentence structure and specific word choices varied more while staying coherent and on-topic. At 1.0, variation was most visible in sentence structure and image pairing (which colors were combined, how the sentence opened), though the outputs never became incoherent for a task this simple. One takeaway: temperature 0 reduces variance but doesn't guarantee a perfectly identical output every run — for tasks needing exact reproducibility, that's an important distinction to keep in mind.

## Which temperature for which use case?

- **Support bot → 0.0–0.2.** Predictability matters most: the same question should get a consistent, reliable answer every time. Even the mild variation seen at temp 0.0 here shows why support bots often need additional consistency techniques beyond just setting temperature to zero.
- **Code generator → 0.0–0.2.** Correctness is binary — code either runs correctly or it doesn't. Low temperature avoids introducing unnecessary variation into otherwise-working patterns.
- **Marketing copy tool → 0.8–1.0.** The goal here is fresh, varied phrasing across multiple draft options — the visible shifts in imagery and structure at temperature 1.0 are exactly the kind of variety you'd want when generating several ad copy options to choose from.