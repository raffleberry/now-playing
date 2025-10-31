import asyncio
import signal
from typing import Sequence

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
)


class Media:
    def __init__(self):
        self.shutdown_flag = False

    async def start(self):
        self.loop = asyncio.get_running_loop()
        signal.signal(signal.SIGINT, self.handle_sigint)

        self.eTokenForSession: dict[str, EventRegistrationToken] = {}
        
        self.mediaSessions: dict[str, MediaSession] = {}

        self.sessionManager: MediaSessionManager = await MediaSessionManager.request_async()

        self.EtokenSessions: EventRegistrationToken = self.sessionManager.add_sessions_changed(self.onSessionsChanged)
        self.processSessions(self.sessionManager.get_sessions())


        await self.waitForSigInt()

        self.releaseAll()

    def handle_sigint(self, signum, frame):
        print("Shutting down...")
        self.shutdown_flag = True

    async def waitForSigInt(self):
        while not self.shutdown_flag:
            await asyncio.sleep(1)
        

    def stop(self):
        self.shutdown_flag = True

    def processSessions(self, sessions: Sequence[MediaSession]):
        sessionsDict = dict((session.source_app_user_model_id, session) for session in sessions)
        currentSessions = [k for k, _ in self.eTokenForSession.items()]
        for k in currentSessions: 
            if k not in sessionsDict:
                print("Session removed - ", k)
                self.releaseSession(self.mediaSessions[k])
        for k, v in sessionsDict.items():
            if k not in self.eTokenForSession.keys():
                print("Session added - ", k)
                print(self.mediaSessions.keys())
                print(self.eTokenForSession.keys())
                self.mediaSessions[k] = v
                self.getProps(v)
                self.eTokenForSession[k] = v.add_media_properties_changed(self.onMediaPropertiesChanged)


    def getProps(self, s: MediaSession):
        props = asyncio.ensure_future(s.try_get_media_properties_async(), loop=self.loop)
        def printx(future: asyncio.Task[MediaProperties | None]):
            props: MediaProperties|None = future.result()
            if props:
                print(s.source_app_user_model_id, " => ", props.title, "::", props.artist, "::" , props.playback_type)

        props.add_done_callback(printx)
    
    def onMediaPropertiesChanged(self, s: MediaSession, args: MediaPropertiesChangedEventArgs):
        print(":::::ON Media Properties Change:::::")
        self.getProps(s)
            
        
        
    def onSessionsChanged(self, sessions: MediaSessionManager, args: SessionsChangedEventArgs):
        print(":::::ON Sessions Change:::::")

        self.processSessions(sessions.get_sessions())

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

m = Media()
asyncio.run(m.start())