# data-science-playground

###### High Frontier

### 1. Board game processing

#### Goal

- having a computable directed graph of *spaces* and *routes* as a representation of the game board

#### Source data

- [game board picture](source_data/board_game_picture.jpg)
- [game rules from the page of the publisher](https://ionsmg.com/pages/downloads)

#### Process

1. Mapping game board picture to a quasi-semantic SVG file
   - mapping *spaces* (and its numerous properties), *routes* between them and some descriptive notes (i.e. site names or flavor text) into SVG objects
   - mapping by hand, using a layered diagram editor that can export to SVG file (DrawIO aka www.diagrams.net)
   - SVG elements can still be pure graphic (i.e. `ellipse` & `path`), but they should encode concepts of the game
2. Transforming quasi-semantic SVG file to domain concepts with underlying support for directed graph
    - example: large `ellipse` is a Site, a small pink `ellipse` is a Lagrange burn space, etc
    - example: black `path` is a bidirectional route between two connected spaces, a white `path` — a one-directional route
    - transformation should be automatic, using some arbitrary convention for the mapping
    - domain objects should abstract away dependency on the concrete graph library
    - underlying graph library should allow: `NetworkX`, `igraph`, `pygraphviz`
3. Mapping text blocks of the SVG file to the names of the nodes & edges of the graph
4. Annotating collinear routes connected to the same Hohmann intersection
    - there is a specific game rule about moving collinearly via Hohmann intersection (and only via them)
    - the fact about collinearity of two routes is not a simple conclusion of the previous step, because SVG mapping have no intention to represent relations between routes
5. Validating the result with game rules
    - example validation rules:
      - every *space* should be accessible, i.e. there should exist a route between *LEO* and the site
      - two *spaces* should have at most 1 route between them
      - every name on the board should be mapped into exactly one *space*
6. Extending the graph by additional information
   - properties other than names of *spaces* & *routes* can be extracted from a specific spreadsheet
   - the domain objects of the graph should have those properties to allow reasoning
7. Saving the domain objects into a persistent and readable format
   - choose the format: YAML? JSON?
