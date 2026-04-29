from os import environ
from pathlib import Path

from Configurables import (
    AlgTimingAuditor,
    AuditorSvc,
    CellIDEncodingFiller,
    GeoSvc,
    MarlinProcessorWrapper,
    TrackMerger,
)
from Gaudi.Configuration import DEBUG, INFO
from k4FWCore import ApplicationMgr, IOSvc
from k4MarlinWrapper.io_helpers import IOHandlerHelper

MISSING_ENCODINGS = {
    "EcalEndcapsCollectionGapHits": "system:0:5,module:5:3,stave:8:4,tower:12:4,layer:16:6,wafer:22:6,slice:28:4,cellX:32:-16,cellY:48:-16",
}

# Collection Names
SI_TRACK_COLL_NAME = "SiTracksCT"
CLU_TRACK_COLL_NAME = "ClupatraTracks"
CANDIDATE_MERGED_TRACKS_NAME = "CandidateMergedTracks"
REFITTED_MERGED_TRACKS_NAME = "RefittedMergedTracks"
REFITTED_MERGED_TRACKS_REL_NAME = "RefittedMergedTracksRelations"

# Paths
DEFAULT_K4GEO_DIR = Path.home() / "promotion" / "code" / "k4geo"
DEFAULT_DATA_DIR = Path.home() / "promotion" / "data"
DATA_DIR = Path(environ.get("dtDir", DEFAULT_DATA_DIR)) / "2026-04-13-tracking"
INPUT_FILE = DATA_DIR / "2026-04-13-fullreco-noECalGap-Clupatra-IF1_REC.edm4hep.root"
OUTPUT_FILE = DATA_DIR / "2026-04-try_track_merging.edm4hep.root"
REL_PATH_2_DET_MOD_COMPACT = "FCCee/ILD_FCCee/compact/ILD_FCCee_v01/ILD_FCCee_v01.xml"

if __name__ == "__main__":
    svcList = []
    algList = []

    iosvc = IOSvc()
    iosvc.Input = str(INPUT_FILE)
    iosvc.Output = str(OUTPUT_FILE)
    svcList.append(iosvc)

    io_handler = IOHandlerHelper(algList, iosvc)
    io_handler.add_reader([str(INPUT_FILE)])
    io_handler.add_edm4hep_writer(str(OUTPUT_FILE))

    geoSvc = GeoSvc("GeoSvc")
    geoSvc.detectors = [
        environ.get("k4geo_DIR", str(DEFAULT_K4GEO_DIR))
        + "/"
        + REL_PATH_2_DET_MOD_COMPACT
    ]
    geoSvc.OutputLevel = INFO
    geoSvc.EnableGeant4Geo = False
    svcList.append(geoSvc)

    # iosvc.CollectionNames = [SI_TRACK_COLL_NAME, CLU_TRACK_COLL_NAME]

    MyFiller = CellIDEncodingFiller("CellIDEncodingFiller")
    MyFiller.CellIDEncodings = MISSING_ENCODINGS
    algList.append(MyFiller)

    MyMerger = TrackMerger(
        "TrackMerger",
        InputSiTracks=SI_TRACK_COLL_NAME,
        OutTracks=CANDIDATE_MERGED_TRACKS_NAME,
    )
    MyMerger.OutputLevel = DEBUG
    algList.append(MyMerger)

    # MyRefitter = RefitFinal(
    #    "RefitFinal",
    #    InputTrackCollectionName=CANDIDATE_MERGED_TRACKS_NAME,
    #    InputRelationCollectionName=[],
    #    OutputTrackCollectionName=REFITTED_MERGED_TRACKS_NAME,
    # )

    MyRefitter = MarlinProcessorWrapper("MyRefitter")
    MyRefitter.ProcessorType = "RefitProcessor"
    MyRefitter.Parameters = {
        "EnergyLossOn": ["true"],
        "FitDirection": ["+1"],
        "InitialTrackErrorD0": ["1e+06"],
        "InitialTrackErrorOmega": ["0.00001"],
        "InitialTrackErrorPhi0": ["100"],
        "InitialTrackErrorTanL": ["100"],
        "InitialTrackErrorZ0": ["1e+06"],
        "InitialTrackState": ["-1"],
        "InputTrackCollectionName": [CANDIDATE_MERGED_TRACKS_NAME],
        "InputTrackRelCollection": [],
        "OutputTrackCollectionName": [REFITTED_MERGED_TRACKS_NAME],
        "OutputTrackRelCollection": [REFITTED_MERGED_TRACKS_REL_NAME],
        "TrackSystemName": ["DDKalTest"],
    }
    MyRefitter.OutputLevel = INFO
    algList.append(MyRefitter)

    io_handler.finalize_converters()

    # Use Gaudi Auditor service to get timing information on algorithm execution
    auditorSvc = AuditorSvc()
    svcList.append(auditorSvc)
    auditorSvc.Auditors = [AlgTimingAuditor()]

    app_mgr = ApplicationMgr(
        TopAlg=algList,
        EvtSel="NONE",
        EvtMax=10,
        ExtSvc=svcList,
        OutputLevel=INFO,
    )

    app_mgr.AuditAlgorithms = True
    app_mgr.AuditTools = True
    app_mgr.AuditServices = True
