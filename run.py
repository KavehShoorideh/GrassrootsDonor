#!/usr/bin/env python
from grassrootsdonor import app
# app.run(debug = True)
app.run(
    host = '0.0.0.0',
    port = 5000
)

# from update_candidate_data import update_candidate_data as updater
# TODO: Add script to run data updater() every midnight
