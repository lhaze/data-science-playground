# How many wraiths are there in the Necropolis of Warsaw?

### Intro
[Wraith: The Oblivion](https://en.wikipedia.org/wiki/Wraith:_The_Oblivion) is a role-playing game in the setting of [World of Darkness](https://en.wikipedia.org/wiki/World_of_Darkness). The key concept of this world assumes that some people stay in their afterlife for some time as ghosts. The whole kind of them comprise the society on its own rights. Let's assume that the represented world is true and sound. If so, what can we tell about demography of the afterlife?

Let's take a look at one Necropolis (that's an analogue to a city in afterlife) with the whole of historical background: the city of Warsaw and its [tragic war history](https://www.google.pl/search?q=site%3Awikipedia.org+warsaw+at+war&oq=site%3Awikipedia.org+warsaw+at+war). There might be some [historic research](#1) to do.

### Questions

Actually, there are two questions:

##### [Part1: date of death](how_many_wraiths_p1.ipynb)
**DoD)** What is the _date of death_ of how many wraiths? DoD defines culture context of a character and certain aspects of his/her social position. The question is the subject of [part 1](how_many_wraiths_p1.ipynb).

##### [Part2: age of death](how_many_wraiths_p2.ipynb)
What is the _age of death_ of how many wraiths across the population of Necropolis? AoD alters demeanor & nature of wraiths' psyche & shadow. This will be the subject of [part 2](how_many_wraiths_p2.ipynb).

Both questions share the same demographic model of getting to the Shadowlands, migrations & depopulation (Ascension/Oblivion/decorpsing) and differs only in entry data. In this part of the article, let's take DoD on the workshop and try to develop a prototypical model of it.

### Approach

Some historic data for demography of Warsaw (population, mortality, etc.) might be found at [Wikipedia](https://pl.wikipedia.org/wiki/Ludno%C5%9B%C4%87_Warszawy) or academic lecture notes. Other might be estimated _a priori_ (ie. afterlife pass away factors). These data can be used to build linear interpolations and a simple model of accumulative values.

Some events of major influence to the problem might be found elsewhere: war slaughters, plagues, [Maelstroms](http://whitewolf.wikia.com/wiki/Maelstrom_(WTO)). These events disrupt linearity of models in the form of spikes or plateaus. Taking it into account, I've decided to model factors using linear interpolations enriched with ephemeral values and encode it in the form of a timeline of datapoints. This concept is implemented in the [timeline module](src/utils/timeline.py). Interpolations that take ephemeral values into account are constructed in the [functools module](src/utils/functools.py)

### Tools

Let's try to do some math in Python.
* [pandas](https://pypi.python.org/pypi/pandas/) to do some data manipulation
* [matplotlib](https://pypi.python.org/pypi/matplotlib) to do some charts
* [ruamel.yaml](https://pypi.python.org/pypi/ruamel.yaml/) for data serialization ([PyYaml](https://pypi.python.org/pypi/PyYAML) won't do, because of "[sequence as a key of mapping](https://stackoverflow.com/questions/13538015/sequence-as-key-of-yaml-mapping-in-python)" problem)
* [some own code](src/utils) written to build a model
