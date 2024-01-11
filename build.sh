#! /bin/bash
(
    mkdir -p /tmp/plugin.video.stash
    rsync -a --exclude 'resources/stash_logo.svg' addon.xml addon.py resources /tmp/plugin.video.stash
    cd /tmp/
    rm -r /tmp/plugin.video.stash/venv
    zip -r plugin.video.stash.zip plugin.video.stash/
    rm -r /tmp/plugin.video.stash
)
mv /tmp/plugin.video.stash.zip .
