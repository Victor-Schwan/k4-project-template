from os import environ
from pathlib import Path

from Configurables import TrackMerger
from Gaudi.Configuration import DEBUG, INFO
from k4FWCore import ApplicationMgr, IOSvc

SI_TRACK_COLL_NAME = "SiTracksCT"
CLU_TRACK_COLL_NAME = "ClupatraTracks"
DEFAULT_DATA_DIR = Path.home() / "promotion/data"

DATA_DIR = Path(environ.get("dtDir", DEFAULT_DATA_DIR)) / "2026-04-13-tracking"

iosvc = IOSvc()
iosvc.Input = str(
    (DATA_DIR / "2026-04-13-fullreco-noECalGap-Clupatra-IF1_REC").with_suffix(
        ".edm4hep.root"
    )
)
iosvc.Output = str(
    (DATA_DIR / "2026-04-try_track_merging").with_suffix(".edm4hep.root")
)

# iosvc.CollectionNames = [SI_TRACK_COLL_NAME, CLU_TRACK_COLL_NAME]

MyMerger = TrackMerger("TrackMerger", InputSiTracks=SI_TRACK_COLL_NAME)
MyMerger.OutputLevel = DEBUG

ApplicationMgr(
    TopAlg=[MyMerger],
    EvtSel="NONE",
    EvtMax=10,
    ExtSvc=[iosvc],
    OutputLevel=INFO,
)
