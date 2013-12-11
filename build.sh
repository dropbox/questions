#!/bin/bash

coffee \
    --compile \
    --output static/js/ \
    --join questions.js \
    coffee/*.coffee
