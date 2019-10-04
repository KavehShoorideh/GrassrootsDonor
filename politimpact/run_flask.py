#!/usr/bin/env python
from politimpact.flaskserver import app
# app.run(debug = True)
app.run(
    host = '127.0.0.1',
    port = 5000
)

# from update_candidate_data import update_candidate_data as updater
# TODO: Add script to run data updater() every midnight
