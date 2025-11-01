import asyncio
from dataclasses import dataclass
from typing import List, Sequence
from np.utils import log
from winrt.windows.foundation import EventRegistrationToken
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSession as MediaSession,
)
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionMediaProperties as MediaProperties
)
from winrt.windows.media.control import (
    MediaPropertiesChangedEventArgs,
    SessionsChangedEventArgs,
)

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal


@dataclass
class PropsData:
    app: str
    title: str
    artist: str
    type: str
    status: str

@dataclass
class SessionsData:
    added: List[str]
    removed: List[str]

class Media(QObject):
    onUpdateMediaSessions = Signal(SessionsData)
    onMediaPropsRefresh = Signal(PropsData)

    def __init__(self):
        super().__init__()
        self.eTokenForSession: dict[str, EventRegistrationToken] = {}
        self.mediaSessions: dict[str, MediaSession] = {}
    
    async def registerLoop(self):
        log.debug("Registering loop")
        self.loop = asyncio.get_event_loop()
        log.debug(self.loop)
        log.debug("Registered loop")
        
    async def start(self):
        log.debug("STARTING Media")
        self.sessionManager: MediaSessionManager = await MediaSessionManager.request_async()
        self.EtokenSessions: EventRegistrationToken = self.sessionManager.add_sessions_changed(self.sessionsChangeHandler)
        self.sessionsChangeHandler(self.sessionManager, None)
        log.debug("STARTED Media")

    def processSessionsx(self, sessions: Sequence[MediaSession]):
        pass
    
    async def grabMediaProperties(self, appId: str):
        s = self.mediaSessions[appId]
        props = await s.try_get_media_properties_async()
        playbackInfo = s.get_playback_info()
        if props:
            type = ""
            if playbackInfo.playback_type:
                type = playbackInfo.playback_type.name
            status = ""
            if playbackInfo.playback_status:
                status = playbackInfo.playback_status.name

            m = PropsData(
                app=s.source_app_user_model_id,
                title=props.title,
                artist=props.artist,
                type=type,
                status=status
            )
            return m


    def mediaPropsChangeHandler(self, s: MediaSession, args: MediaPropertiesChangedEventArgs | None):
        log.debug(":::::ON Media Properties Change:::::")
        self.onMediaPropsRefresh.emit(s.source_app_user_model_id)
        
    def sessionsChangeHandler(self, sm: MediaSessionManager, args: SessionsChangedEventArgs | None):
        log.debug(":::::ON Sessions Change:::::")
        sessions = sm.get_sessions()
        sessionsDict = dict((session.source_app_user_model_id, session) for session in sessions)
        currentSessions = [k for k, _ in self.eTokenForSession.items()]
        added, removed = [], []
        for k in currentSessions: 
            if k not in sessionsDict:
                log.debug(f"Session removed - {k}")
                self.releaseSession(self.mediaSessions[k])
                removed.append(k)
        for k, v in sessionsDict.items():
            if k not in self.eTokenForSession.keys():
                log.debug(f"Session added - {k}")
                self.mediaSessions[k] = v
                self.mediaPropsChangeHandler(v, None)
                self.eTokenForSession[k] = v.add_media_properties_changed(self.mediaPropsChangeHandler)
                added.append(k)
        
        self.onUpdateMediaSessions.emit(SessionsData(added=added, removed=removed))

    def releaseAll(self):
        for k, v in self.eTokenForSession.items():
            self.mediaSessions[k].remove_media_properties_changed(v)
        self.mediaSessions = {}
        self.sessionManager.remove_sessions_changed(self.EtokenSessions)

    def releaseSession(self, session: MediaSession):
        id = session.source_app_user_model_id
        self.mediaSessions[id].remove_media_properties_changed(self.eTokenForSession[id])
        self.eTokenForSession.pop(id)
        self.mediaSessions.pop(id)

