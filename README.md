# data-science-playground

###### Let's have some fun with a set of libs & approaches.
Here is a bunch of my toy projects on topic such as data processing, data mining & process modelling. All flavored with my geeky hobbies.

Under development:
---
#### [how_many_wraiths](how_many_wraiths)
* modelling population dynamics within alternate-reality fantasy setting
* basic research on historic data of demography
* some utility code for models
* simple data visualization
* `pandas`, `matplotlib`/`pylab`, `YAML`

#### [jats](jats)
* medical journal articles in PDF format as an input
* automation of conversion from PDF to semantic XML ([JATS](https://en.wikipedia.org/wiki/Journal_Article_Tag_Suite))
* pipelining and clustering the process
* long term goal to introduce some [NLP](https://en.wikipedia.org/wiki/Natural-language_processing)-jutsu and rule-based domain system into the process to leverage the quality of semantic markup
* `pdfx`, `requests`, `lxml`, `PySpark`

#### [rising_sun](rising_sun)
* process modelling using programming in logic (Datalog±)
* automated planning and plan revision
* multiagent system of players using [InteRRaP](https://www.dfki.de/web/forschung/publikationen/renameFileForDownload?filename=RR-93-26.pdf&file_id=uploads_1751) architecture (an ancient design of [DAI](https://en.wikipedia.org/wiki/Distributed_artificial_intelligence))
* the theme of the process is a board game of [Rising Sun](https://boardgamegeek.com/boardgame/205896/rising-sun)
* input: game rules, game setup configuration, bot attunement
* output: a Datalog program for planning & plan execution
* side-effect: an AI for the game
* `pyDatalog`, `SQLAlchemy`, `colander` & own model micro-framework, `asciimatics`

Ideas:
---
#### trajectory
* simulation of trajectories of space vehicles within Solar system
* modelling the kinetics of [orbital mechanics](https://en.wikipedia.org/wiki/Orbital_mechanics)
* visualization via animations
* `simpy`, `PyEphem`, `sky-charts`, `Gizeh`, `MoviePy`/`visual`

#### github analysis
* heuristic static code analysis & machine reasoning about code
* information retrieval and extraction via GitHub API
* find repos with some kind of pattern (some vulnerability and a living webapp?)
* [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) analysis
* application of a IR storage
* `github3`, `PySpark`, `ast`, `elasticsearch`

#### emergency on the website
* user behavior modelling on a complex domain: web traffic analysis, website security
* information extraction from nginx/webapp logs
* modelling concepts of harmful user activity
* multi-layer rule-based rough classifiers
* `PySpark`, log parsing, `scikit-learn`

#### Jupiter clouds recognition
* physics-based visual data analysis
* input: rendered picture of clouds on Jupiter
* extraction of information about wind streams from cloud color data
* output: map of low-speed areas in the upper layers of the atmosphere of the Jupiter
* `opencv`

#### facebook/twitter bot-finder
* user behavior modelling on a complex domain: social media
* input: posts/comments/tweets of users of some given group
* finding cliques and/or separated users with some given bevioral pattern
* temporal evolutions of patterns; post-factum behavior analysis
* output: a list of bot-user candidates
* website API, `PySpark`, `nltk`, `scikit-learn`, some pattern recognition
