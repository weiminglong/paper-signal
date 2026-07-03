# arXiv category cheat-sheet (plain topic → code)

- AI / agents / LLMs → `cs.AI`, `cs.CL`
- Machine learning / deep learning → `cs.LG`, `stat.ML`
- NLP / language → `cs.CL`
- Computer vision / images → `cs.CV`
- Robotics → `cs.RO`
- Multi-agent systems → `cs.MA`, `cs.AI`
- Speech / audio / music → `cs.SD`, `eess.AS`
- Security / cryptography → `cs.CR`
- Human-computer interaction → `cs.HC`
- Information retrieval / search / recsys → `cs.IR`
- Software engineering → `cs.SE`
- Systems / distributed → `cs.DC`, `cs.OS`
- Biology → `q-bio.*`: neuroscience `q-bio.NC`, genomics & gene editing `q-bio.GN`, proteins &
  molecular structure (AlphaFold-style) `q-bio.BM`, quantitative methods `q-bio.QM`, molecular
  networks `q-bio.MN`, cell behavior `q-bio.CB`
- Economics / econometrics → `econ.EM` (econometrics), `econ.TH` (theory), `econ.GN` (general);
  causal inference often lives in `stat.ME`
- Finance / quant / markets → `q-fin.*`: trading & microstructure `q-fin.TR`, mathematical
  finance `q-fin.MF`, portfolio `q-fin.PM`, risk `q-fin.RM`, computational `q-fin.CP`
- Game theory / mechanism design / auctions → `cs.GT`, `econ.TH`
- Statistics / causal inference → `stat.ME` (methodology), `stat.AP` (applied), `stat.ML`
- Climate / earth science → `physics.ao-ph` (atmospheric & oceanic), `physics.geo-ph`
  (geophysics); attribution/impact methods often `stat.AP`
- Astronomy / astrophysics → `astro-ph.*`: exoplanets `astro-ph.EP`, high-energy
  `astro-ph.HE`, instrumentation & surveys `astro-ph.IM`, stellar `astro-ph.SR`, galaxies
  `astro-ph.GA`, cosmology `astro-ph.CO`; **gravitational waves → `gr-qc`** (+ astro-ph.HE)
- Cryptocurrency / blockchain / DeFi → `cs.CR` + `q-fin.TR` (note: "crypto" here is NOT
  just cryptography — include blockchain/market keywords, not only cs.CR)
- Education / edtech / AI for learning → `cs.CY` + `cs.HC` (+ `cs.CL` for tutoring/LLM work)
- Chemistry / chemical physics / synthesis / catalysis → `physics.chem-ph` +
  `cond-mat.mtrl-sci`; ML-for-molecules cross-posts to `cs.LG` (+ `q-bio.BM` for
  biomolecules)
- Social networks / computational social science / opinion dynamics / misinformation →
  `cs.SI`, `physics.soc-ph` (+ `cs.CY` for platforms & society)
- Materials science / batteries / solar cells → `cond-mat.mtrl-sci` (+ `cond-mat.soft`,
  `cond-mat.supr-con` as fits); ML-for-materials also cross-posts to `cs.LG`
- Digital humanities / historical documents / cultural heritage → `cs.CL` + `cs.CV` +
  `cs.DL` (digital libraries) + `cs.CY`; HTR/OCR work often lands in `cs.CV` and `cs.DL`
- Other physics / math → the specific `physics.*` / `math.*` subcategory — but check the
  domain-specific archives first (`cond-mat.*`, `astro-ph.*`, `q-bio.*`, `q-fin.*`); many
  fields do NOT live under `physics.*`

If a topic isn't listed, pick the closest code or ask the user to clarify the field. For a
cross-cutting theme with no home category (e.g. "evaluation", "benchmarks"), model it as
**keywords** across the relevant categories rather than a category of its own. Papers are often
cross-posted, so listing 2–3 categories per domain (not one) catches more of the real work —
e.g. market microstructure lives under `q-fin.TR` far more than `econ.*`.
