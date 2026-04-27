from pathlib import Path

from Configurables import TrackD0Printer
from Gaudi.Configuration import INFO
from k4FWCore import ApplicationMgr, IOSvc

SI_TRACK_COLL_NAME = "SiTracksCT"
CLU_TRACK_COLL_NAME = "ClupatraTracks"

iosvc = IOSvc()
iosvc.Input = str(
    (
        Path.home()
        / "promotion/data"
        / "2026-04-13-tracking/2026-04-13-fullreco-noECalGap-Clupatra-IF1_REC"
    ).with_suffix(".edm4hep.root")
)

iosvc.CollectionNames = [SI_TRACK_COLL_NAME, CLU_TRACK_COLL_NAME]

printer = TrackD0Printer(
    "TrackD0Printer", nStars=40, InputSiTracks=[SI_TRACK_COLL_NAME]
)
printer.OutputLevel = INFO

ApplicationMgr(
    TopAlg=[printer],
    EvtSel="NONE",
    EvtMax=10,
    ExtSvc=[iosvc],
    OutputLevel=INFO,
)
