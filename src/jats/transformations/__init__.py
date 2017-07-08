# TEXT CLEANING
# remove "- " throughout the text
# push tails of <marker type="block"/> into sections

# ENGLISH VERSION
# push tails of <marker type="column" number="2"/> to separate tag

# REFERENCES
# split references
# look for <xref>

# ARTICLE META
# split authors and push them into <contrib-group><contrib contrib-type="author">
# building affiliates

from .base import Transformation