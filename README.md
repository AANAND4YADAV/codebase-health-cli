

## Experimental Disclaimer

This project is an **AI-assisted software engineering experiment** exploring codebase analysis, maintainability metrics, and developer tooling.

### Limitations

* Heuristics for non-Python languages are approximate.
* Duplicate code detection uses line-block hashing rather than semantic clone analysis.
* Scoring thresholds are opinionated defaults and should not be considered industry standards.
* Features, metrics, and APIs may evolve as the project develops.

### Intended Use

Use this tool as:

* A learning resource
* A quick codebase health snapshot
* An exploration of software quality metrics
* A foundation for further experimentation

It is **not intended to be a production-grade static analysis platform** or a strict CI/CD quality gate without additional validation.

---

## Supported File Types

The tool currently supports analysis across the following file types:

```text
.py  .js  .ts  .tsx  .jsx
.java  .go  .rs  .rb  .php
.c  .cpp  .h  .hpp  .cs
.swift  .kt  .scala
.sh  .sql
.yaml  .yml  .toml  .json
.md
```

### Notes

* Complexity analysis is currently Python-specific.
* Naming analysis is currently Python-specific.
* Other metrics operate across the broader supported file set.

---

## Author

**AANAND4YADAV**

Built through curiosity, experimentation, and AI collaboration.

---

## License

Experimental project — use, modify, and explore at your own discretion.
