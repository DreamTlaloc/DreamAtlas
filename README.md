# DreamAtlas
Dominions 6 map generator

DreamAtlas is an open-source Python library for Dominions 6 map editing and generation.  DreamAtlas allows users to seamlessly interact with Dominions maps through Python code. Equipped with groundbreaking map generation algorithms and tools for artists that will allow maps to be made better than ever before.

I've always loved fantasy, and a major part of fantasy for me is elaborate maps, epic mountain ranges, rivers and so on. I also love competition and multiplayer strategy games. Dominions has never really brought this together for me, most maps are either focused on nice geography or good balance (or neither in vanilla), so I decided to make my own map generator to make the kind of maps I'd like to play on. This meant going to the drawing board and really asking what makes a good dominions map and what maths you need to accomplish that? Further I wanted to make a tool not just to make maps, but to make map generators and support people making maps from custom art, as a result the DreamAtlas generator is essentially just a script calling functions and classes from the DreamAtlas library, anyone with some python knowledge could make their own mapmaker with DreamAtlas using the generalised tools, classes and methods it comes with.


# Install

Clone this repository, and run `run.py` or directly install this with either `pip` or `pipx`

```
pipx install .
# OR (after obtaining all the dependencies)
pip install . --break-system-packages
```

# Examples

There's a usage example of DreamAtlas as a library available at `examples/script.py`


For Windows users, there's builds available at https://tlaloca.itch.io/dreamatlas
