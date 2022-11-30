# immersion
An algorithm that generates video art, given an audio file and a set of pictures, with a single command.

It extracts transients and other audio features/events and feeds them into a State Machine. The latter uses Super-resolution and Neural Style Transfer, as well as image transformations (hue, saturation, etc) and randomness, to produce video frames.

Directory operations were not fully incorporated into the code so they may need some tweaking to work with new content.
