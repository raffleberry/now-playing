from dataclasses import dataclass
from typing import List

from PySide6.QtCore import QObject, Signal
from winrt.windows.foundation import EventRegistrationToken
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSession as MediaSession,
)
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionMediaProperties as MediaProperties,
)
from winrt.windows.media.control import (
    MediaPropertiesChangedEventArgs,
    SessionsChangedEventArgs,
    PlaybackInfoChangedEventArgs,
)

from winrt.windows.storage.streams import IRandomAccessStreamReference, DataReader

from np.utils import log


@dataclass
class MediaData:
    app: str
    title: str
    artist: str
    thumbnail: bytes

@dataclass
class SessionsData:
    added: List[str]
    removed: List[str]

@dataclass
class PlaybackData:
    app: str
    playback_status: str
    is_play_pause_toggle_enabled: bool
    is_next_enabled: bool
    is_previous_enabled: bool


class Media(QObject):
    onUpdateMediaSessions = Signal(SessionsData)
    onMediaPropsRefresh = Signal(MediaData)
    onPlaybackInfoRefresh = Signal(PlaybackData)

    def __init__(self):
        super().__init__()
        self.eTokenForMediaData: dict[str, EventRegistrationToken] = {}
        self.mediaSessions: dict[str, MediaSession] = {}
        self.playbackInfo: dict[str, PlaybackData] = {}
        self.eTokenForPlaybackData: dict[str, EventRegistrationToken] = {}
    
    async def start(self):
        log.debug("STARTING Media")

        self.sessionManager: MediaSessionManager = await MediaSessionManager.request_async()
        self.EtokenForSessionManager: EventRegistrationToken = self.sessionManager.add_sessions_changed(self.sessionsChangeHandler)
        self.sessionsChangeHandler(self.sessionManager, None)
        
        log.debug("STARTED Media")

    async def read_stream_reference_to_bytes(self, stream_ref: IRandomAccessStreamReference) -> bytes:
        stream = await stream_ref.open_read_async()

        reader = DataReader(stream)
        size = stream.size

        await reader.load_async(size)

        buffer = reader.read_buffer(size)
        data = bytes(buffer)

        reader.close()
        stream.close()
        return data

    async def grabMediaProperties(self, appId: str):
        s = self.mediaSessions[appId]
        props = await s.try_get_media_properties_async()
        if props:
            thumbnail = b""
            if props.thumbnail:
                thumbnail = await self.read_stream_reference_to_bytes(props.thumbnail)
            m = MediaData(
                app=s.source_app_user_model_id,
                title=props.title,
                artist=props.artist,
                thumbnail=thumbnail,
            )
            return m

    async def prev(self, appId: str):
        s = self.mediaSessions[appId]
        await s.try_skip_previous_async()

    async def pausePlay(self, appId: str):
        s = self.mediaSessions[appId]
        await s.try_toggle_play_pause_async()

    async def next(self, appId: str):
        s = self.mediaSessions[appId]
        await s.try_skip_next_async()

    def mediaPropsChangeHandler(self, s: MediaSession, args: MediaPropertiesChangedEventArgs | None):
        log.debug(":::::ON Media Properties Change:::::")
        self.onMediaPropsRefresh.emit(s.source_app_user_model_id)
    
    def playbackInfoChangeHandler(self, s: MediaSession, args: PlaybackInfoChangedEventArgs | None):
        log.debug(":::::ON Playback Info Change:::::")
        info = s.get_playback_info()
        p = PlaybackData(
            app=s.source_app_user_model_id,
            playback_status=info.playback_status.name,
            is_play_pause_toggle_enabled=info.controls.is_play_pause_toggle_enabled,
            is_next_enabled=info.controls.is_next_enabled,
            is_previous_enabled=info.controls.is_previous_enabled,
        )
        self.playbackInfo[s.source_app_user_model_id] = p
        self.onPlaybackInfoRefresh.emit(p)

    def timelinePropsChangeHandler(self, s: MediaSession, args: MediaPropertiesChangedEventArgs | None):
        log.debug(":::::ON Timeline Properties Change:::::")

    def sessionsChangeHandler(self, sm: MediaSessionManager, args: SessionsChangedEventArgs | None):
        
        log.debug(":::::ON Sessions Change:::::")
        
        sessions = sm.get_sessions()
        sessionsDict = dict((session.source_app_user_model_id, session) for session in sessions)
        currentSessions = [k for k, _ in self.eTokenForMediaData.items()]
        added, removed = [], []
        for k in currentSessions: 
            if k not in sessionsDict:
        
                log.debug(f"Session removed - {k}")
        
                self.releaseSession(self.mediaSessions[k])
                removed.append(k)
        for k, v in sessionsDict.items():
            if k not in self.eTokenForMediaData.keys():
        
                log.debug(f"Session added - {k}")
        
                self.mediaSessions[k] = v
                self.mediaPropsChangeHandler(v, None)
                self.playbackInfoChangeHandler(v, None)
                self.eTokenForMediaData[k] = v.add_media_properties_changed(self.mediaPropsChangeHandler)
                self.eTokenForPlaybackData[k] = v.add_playback_info_changed(self.playbackInfoChangeHandler)
                added.append(k)
        
        self.onUpdateMediaSessions.emit(SessionsData(added=added, removed=removed))

    def releaseAll(self):
        self.sessionManager.remove_sessions_changed(self.EtokenForSessionManager)
        sessions = [v for _, v in self.mediaSessions.items()]
        for s in sessions:
            self.releaseSession(s)

    def releaseSession(self, session: MediaSession):
        id = session.source_app_user_model_id
        self.mediaSessions[id].remove_playback_info_changed(self.eTokenForPlaybackData[id])
        self.mediaSessions[id].remove_media_properties_changed(self.eTokenForMediaData[id])
        self.eTokenForMediaData.pop(id)
        self.mediaSessions.pop(id)
        self.playbackInfo.pop(id)

