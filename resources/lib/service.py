"""Reports playback in Kodi back to Stash, like Stash' own player does:
play count (after the minimum play percent set in Stash), resume point and
play duration."""
import re
import time
import urllib.parse
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.stash_interface import StashInterface

SCENE_PATH = re.compile(r'/scene/(\d+)/stream')
SAVE_INTERVAL = 30
# Like Stash' player: playing (almost) to the end clears the resume point
FINISHED_PERCENT = 98
PLAYING_PROPERTY = 'plugin.video.stash.playing_scene'
# "<scene id>:<seconds>", set by play_from when the user chooses to resume
START_OFFSET_PROPERTY = 'plugin.video.stash.start_offset'
SERVICE_PROPERTY = 'plugin.video.stash.service'


def log(message: str):
    xbmc.log('[plugin.video.stash] ' + message, xbmc.LOGINFO)


def client() -> (StashInterface, str):
    addon = xbmcaddon.Addon()
    base_url = addon.getSetting('base_url')
    return StashInterface(base_url, addon.getSetting('api_key')), urllib.parse.urlparse(base_url).netloc


class Session:
    def __init__(self, stash: StashInterface, scene_id: str, total: float, ui: dict):
        self.stash = stash
        self.scene_id = scene_id
        self.total = total
        self.track = ui.get('trackActivity', True) is not False
        self.minimum_percent = float(ui.get('minimumPlayPercent') or 0)
        self.position = 0.0
        self.unsaved = 0.0
        self.watched = 0.0
        self.last_save = time.monotonic()
        self.counted = False

    def tick(self, position: float, elapsed: float):
        self.position = position
        self.unsaved += elapsed
        self.watched += elapsed
        if not self.counted and self.track and self.total > 0 \
                and self.watched / self.total * 100 >= self.minimum_percent:
            self.counted = True
            self.stash.scene_add_play(self.scene_id)
        if time.monotonic() - self.last_save >= SAVE_INTERVAL:
            self.save()

    def save(self, ended: bool = False):
        self.last_save = time.monotonic()
        if not self.track:
            return
        finished = ended or (self.total > 0 and self.position / self.total * 100 >= FINISHED_PERCENT)
        self.stash.scene_save_activity(self.scene_id, 0.0 if finished else self.position, self.unsaved)
        self.unsaved = 0.0


class Player(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)
        self.session = None
        self.ended = False

    def onAVStarted(self):
        self.finish()
        try:
            playing = self.getPlayingFile()
            (stash, netloc) = client()
            url = urllib.parse.urlparse(playing)
            match = SCENE_PATH.search(url.path)
            if match is None or url.netloc != netloc:
                return
            self.session = Session(stash, match.group(1), self.getTotalTime(), stash.ui_configuration())
            self.ended = False
            window = xbmcgui.Window(10000)
            window.setProperty(PLAYING_PROPERTY, self.session.scene_id)
            (offset_scene, _, offset) = window.getProperty(START_OFFSET_PROPERTY).partition(':')
            window.clearProperty(START_OFFSET_PROPERTY)
            if offset_scene == self.session.scene_id:
                self.seekTime(float(offset))
        except Exception as e:
            log('could not start tracking: {}'.format(e))
            self.session = None

    def onPlayBackEnded(self):
        self.ended = True
        self.finish()

    def onPlayBackStopped(self):
        self.finish()

    def onPlayBackError(self):
        self.finish()

    def onPlayBackPaused(self):
        self.save()

    def save(self):
        if self.session is not None:
            try:
                self.session.save()
            except Exception as e:
                log('could not save activity: {}'.format(e))

    def finish(self):
        if self.session is None:
            return
        session, self.session = self.session, None
        xbmcgui.Window(10000).clearProperty(PLAYING_PROPERTY)
        try:
            session.save(ended=self.ended)
        except Exception as e:
            log('could not save activity: {}'.format(e))

    def poll(self, elapsed: float):
        if self.session is None or not self.isPlayingVideo():
            return
        try:
            if xbmc.getCondVisibility('Player.Paused'):
                self.session.position = self.getTime()
            else:
                self.session.tick(self.getTime(), elapsed)
        except Exception as e:
            log('could not report playback: {}'.format(e))


def run():
    # Kodi can start the service just after the add-on was disabled (or start it twice when it is
    # disabled and enabled quickly); such an instance never gets an abort request and would keep
    # Kodi from shutting down and report playback twice. The newest instance wins.
    token = str(time.time())
    window = xbmcgui.Window(10000)
    window.setProperty(SERVICE_PROPERTY, token)
    log('playback reporting started')
    monitor = xbmc.Monitor()
    player = Player()
    last = time.monotonic()
    while not monitor.waitForAbort(1):
        if window.getProperty(SERVICE_PROPERTY) != token \
                or not xbmc.getCondVisibility('System.AddonIsEnabled(plugin.video.stash)'):
            break
        now = time.monotonic()
        player.poll(now - last)
        last = now
    player.finish()
    log('playback reporting stopped')
