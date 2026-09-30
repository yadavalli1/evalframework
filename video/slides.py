"""Slide content and narration for the paper-review video. Each slide: (html_body, narration)."""

ARCH = open(__file__.replace("slides.py", "architecture.svg")).read()


def bullets(*items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def fig(path, caption):
    return f'<div class="fig"><img src="../../paper/figures/{path}"><p class="cap">{caption}</p></div>'


SLIDES = [
    (
        """<div class="title">
          <p class="kicker">Paper review</p>
          <h1>Building an LLM Evaluation Framework</h1>
          <h2>Architecture, Statistics, and Practice</h2>
          <p class="meta">Evalframework Project · Technical report · September 2026</p></div>""",
        "Welcome. In this video we review the report, Building an LLM Evaluation Framework: Architecture, Statistics, and Practice. "
        "It's a design guide for teams who want eval numbers they can actually act on. "
        "We'll walk through the architecture it proposes, the statistics it argues should be built in, "
        "how it treats L L M judges, and then give our own assessment of its strengths and gaps.",
    ),
    (
        "<h1>The problem</h1>"
        + bullets(
            "Outputs are <b>open-ended</b>: “correct” often has no string-equality definition",
            "One model, <b>thousands of tasks</b>: no single benchmark describes it",
            "The unit under test is a <b>pipeline</b>: prompt + retriever + tools + agent loop",
            "Typical internal evals: <b>no error bars</b>, <b>unvalidated graders</b>, <b>possibly contaminated data</b>",
        ),
        "The paper starts from a simple observation. Classical machine learning had a held-out test set and one metric. "
        "L L Ms break that in three ways. Outputs are open-ended, so correctness is often not a string match. "
        "The same model serves thousands of tasks. And what we ship is usually a pipeline, not a bare model. "
        "Meanwhile, most internal evals are ad-hoc scripts with no error bars, graders nobody validated, and data that may have leaked into training.",
    ),
    (
        "<h1>Seven requirements</h1>"
        '<div class="grid2">'
        + bullets(
            "<b>R1 Reproducible</b> — every score traceable",
            "<b>R2 Statistically honest</b> — intervals &amp; tests",
            "<b>R3 Composable</b> — plug in tasks, models, scorers",
            "<b>R4 Grader-validated</b> — judges checked vs humans",
        )
        + bullets(
            "<b>R5 Sliceable</b> — no averages hiding regressions",
            "<b>R6 Pipeline-aware</b> — RAG &amp; agents, not just models",
            "<b>R7 Cheap to run often</b> — cache, tiers, CI",
        )
        + "</div>",
        "From those failure modes, the authors derive seven requirements. "
        "Results must be reproducible, and statistically honest. The framework should be composable, "
        "and any model-based grader must be validated against humans. "
        "Results need to be sliceable, so an average can't hide a regression. "
        "The system under test can be a whole pipeline. And evals must be cheap enough to run on every change.",
    ),
    (
        '<h1>Reference architecture</h1><div class="svgwrap">' + ARCH + "</div>",
        "Here is the core of the paper: a seven-part architecture. "
        "In blue is what gets evaluated: a declarative task spec and a versioned dataset with slice metadata and cluster I Ds. "
        "In orange is how it runs: a model adapter that can wrap a model, a RAG system, or an agent, and a runner with concurrency, retries, and a response cache. "
        "In green is how it's judged: scorers, a statistical aggregator, and reports with C I gates. "
        "Underneath everything is a content-addressed run record. Hash the task, data, prompt, model, parameters, scorer, and seed, "
        "and two runs with the same hash are the same experiment. That single design choice is what makes every past number auditable.",
    ),
    (
        "<h1>Scorers: cheapest reliable first</h1>"
        '<ol class="ladder">'
        "<li><b>Programmatic</b> — exact match, regex, JSON schema, unit tests, verifiable constraints</li>"
        "<li><b>Reference similarity</b> — BLEU, ROUGE, BERTScore: regression tripwires</li>"
        "<li><b>LLM-as-judge</b> — flexible, but a measurement instrument to validate</li>"
        "<li><b>Human review</b> — ground truth for subjective quality; the calibration target</li></ol>"
        '<p class="note">Principle: <b>decompose, then check</b>. Split “is this good?” into checkable criteria.</p>',
        "For scoring, the paper ranks four families. Programmatic checks come first: exact match, regex, schema validation, unit tests. They're deterministic and cheap. "
        "Reference similarity metrics like BLEU and ROUGE are useful mainly as tripwires. "
        "L L M judges are flexible, but the paper insists they're instruments that must be validated. "
        "And human review is the ground truth that calibrates everything else. "
        "The guiding principle is: decompose, then check. Break a fuzzy notion of quality into criteria you can check individually.",
    ),
    (
        "<h1>Every score is an estimate</h1>"
        + fig("fig2_power.png", "Analytic. Baseline accuracy 70%.")
        + '<p class="stat"><b>100 items → ±9.0 pp</b> &nbsp;·&nbsp; 400 → ±4.5 pp &nbsp;·&nbsp; 1,000 → ±2.8 pp</p>',
        "The statistics section is where the paper is most valuable. Every score is an estimate from a finite sample. "
        "On the left: at seventy percent accuracy, a one-hundred-item eval has a ninety-five percent confidence interval of plus or minus nine points. "
        "You need about a thousand items to get under three. "
        "On the right is the fix for comparisons: pair them. Score both systems on the same items and analyze per-item differences. "
        "At a thousand items, the smallest detectable difference drops from five point seven points to four point one when the correlation is point five. "
        "That's the same as halving the sample size you need, and it costs nothing to implement.",
    ),
    (
        "<h1>Clustered items and power analysis</h1>"
        '<div class="split">'
        + fig("fig3_cluster.png", "SE inflation = √(1 + (m − 1)·ICC). Analytic.")
        + "<div>"
        + bullets(
            "10 items per cluster, ICC 0.2 → true SE is <b>1.67×</b> naive",
            "A “95%” interval then covers only <b>~76%</b>",
            "Fix: store a <b>cluster ID</b>; use cluster-robust SEs",
            "Plan <b>n</b> from the smallest difference δ that changes the decision",
        )
        + "</div></div>",
        "Two more statistical points. First, items are often clustered, like ten questions about one document. "
        "With ten items per cluster and a modest intra-cluster correlation of point two, the real standard error is one point six seven times the naive one. "
        "So your ninety-five percent interval actually covers about seventy-six percent. The fix is just to store a cluster I D and compute cluster-robust errors. "
        "Second, do power analysis before you build the dataset. Start from the smallest difference that would change your decision, and derive the number of items from it.",
    ),
    (
        "<h1>A noisy judge shrinks real differences</h1>"
        '<div class="split">'
        + fig("fig4_judge.png", "Seeded Monte Carlo: 2,000 evals × 1,000 items, true Δ = 5 pp.")
        + "<div>"
        + bullets(
            "Measured Δ = <b>(2a − 1) · true Δ</b>",
            "Judge agreement a = 0.8 → 5 pp looks like <b>~3 pp</b>",
            "95% band <b>−1.1 to 7.2 pp</b>: includes zero",
            "Halving (2a − 1) needs <b>~4×</b> the items",
        )
        + "</div></div>",
        "The most memorable result concerns L L M judges. If a judge agrees with ground truth with probability a, and errors are symmetric, "
        "the measured difference between two systems is two a minus one, times the true difference. "
        "The paper checks this with a seeded simulation. A judge with eighty percent agreement turns a real five-point improvement into about three points, "
        "and across replicate runs the range includes zero. So the improvement is no longer reliably detectable at a thousand items. "
        "Judge quality trades directly against sample size.",
    ),
    (
        "<h1>Calibrating the judge</h1>"
        '<ol class="ladder">'
        "<li><b>Gold set:</b> 100–300 expert labels across systems and quality levels</li>"
        "<li><b>Agreement:</b> accuracy, Cohen’s κ, confusion matrix</li>"
        "<li><b>Bias tests:</b> position swap flip-rate, length regression, self-preference</li>"
        "<li><b>Mitigate:</b> both orders, binary rubrics, reason-then-verdict, other-family judge</li>"
        "<li><b>Re-validate</b> when judge, prompt, or data changes</li></ol>",
        "So the paper gives a calibration protocol. Build a gold set of a few hundred expert labels. "
        "Measure agreement with accuracy, Cohen's kappa, and a confusion matrix, which tells you whether errors are symmetric noise or one-sided bias. "
        "Test for position bias by swapping answer order, and for verbosity bias by regressing scores on length. "
        "Mitigate with both orderings, simple binary rubrics, reasoning before the verdict, and a judge from a different model family. "
        "And re-validate whenever anything changes.",
    ),
    (
        "<h1>Data integrity, RAG &amp; agents</h1>"
        '<div class="grid2">'
        + "<div><h3>Contamination</h3>"
        + bullets("Private held-out sets", "Canary strings", "Exchangeability tests", "Fresh, post-cutoff items", "Perturbation checks")
        + "</div><div><h3>Pipelines</h3>"
        + bullets("RAG: retrieval, grounding, answer — separately", "Agents: sandboxed, resettable environments", "Score the <b>final state</b>, not the transcript", "Report pass@k <i>and</i> pass^k", "Cost per success")
        + "</div></div>",
        "The paper then covers data integrity. Public benchmarks may be in training data, so keep private held-out sets, "
        "embed canary strings, use statistical contamination tests, and add fresh items. "
        "For RAG, it recommends scoring retrieval, grounding, and answer quality separately, so you can localize failures. "
        "For agents: sandboxed, resettable environments, scoring the final state rather than the transcript, "
        "repeated trials reported as both pass at k and pass hat k, and cost per success.",
    ),
    (
        "<h1>Evals as regression tests</h1>"
        + bullets(
            "<b>Tiers:</b> smoke (every commit) · regression (every merge) · full (every release)",
            "<b>Gates are tests:</b> fail if lower CI of (B − A) &lt; −δ on critical slices",
            "“Score must not drop” fires on noise <b>~50%</b> of the time",
            "<b>Online loop:</b> score production samples; failures become new items",
            "<b>Read transcripts</b>, especially discordant pairs",
        ),
        "Operationally, the paper recommends three tiers: a smoke tier on every commit, a regression tier on every merge, and a full tier with human review before release. "
        "Gates should be statistical tests, not raw comparisons. A rule like 'the score must not drop' fires on pure noise about half the time. "
        "Instead, fail only if the lower confidence bound of the paired difference falls below your threshold. "
        "Close the loop with production traffic, and always read transcripts.",
    ),
    (
        "<h1>Our assessment</h1>"
        '<div class="grid2">'
        + '<div><h3 class="good">Strengths</h3>'
        + bullets(
            "Treats evaluation as <b>measurement</b>, with numbers",
            "Clean separation: what / how run / how judged",
            "Run record gives real reproducibility",
            "Concrete, adoptable task spec and checklist",
            "Well grounded in literature (32 refs)",
        )
        + '</div><div><h3 class="warn">Gaps</h3>'
        + bullets(
            "No experiments on <b>real models or judges</b>",
            "Judge model assumes <b>symmetric</b> noise",
            "Large-sample approximations for small evals",
            "Architecture is a design, <b>not yet code</b>",
            "Little on multimodal or safety-specific evals",
        )
        + "</div></div>",
        "Now our assessment. The main strength is that the paper treats evaluation as measurement, and backs that up with numbers anyone can reproduce. "
        "The architecture's separation of concerns is clean, and the content-addressed run record is a genuinely practical idea. "
        "The task spec and checklist can be adopted directly. "
        "On the other side, there are no experiments with real models or real judges, so the calibration protocol is untested in practice. "
        "The judge analysis assumes symmetric noise, while real judges are also biased. "
        "The power formulas are large-sample approximations. And the architecture is a design, not yet an implementation. "
        "A reference implementation, with a case study on a real task, would be the natural next step.",
    ),
    (
        "<h1>Takeaways</h1>"
        '<ol class="ladder big">'
        "<li>A 100-item eval can’t see differences under <b>~10 points</b></li>"
        "<li>Compare systems with <b>paired</b> tests, by default</li>"
        "<li>Store <b>cluster IDs</b>; use cluster-robust errors</li>"
        "<li>An 80%-agreement judge can hide a real <b>5-point</b> gain: calibrate it</li>"
        "<li>Hash everything into a <b>run record</b></li></ol>"
        '<p class="note">Paper, figures, and this video: <code>paper/</code> and <code>video/</code> in the evalframework repo</p>',
        "To wrap up, five takeaways. A hundred-item eval can't see differences under about ten points. "
        "Compare systems with paired tests by default. Store cluster I Ds and use cluster-robust errors. "
        "Calibrate your judges, because an eighty percent judge can hide a real five-point gain. "
        "And hash everything into a run record so every number is reproducible. "
        "The paper, its figures, and the scripts that generate them are all in the repository. Thanks for watching.",
    ),
]
