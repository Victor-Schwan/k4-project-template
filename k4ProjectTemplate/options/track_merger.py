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
CANDIDATE_GREEDY_MERGED_TRACKS_NAME = "CandidateMergedTracks"
REFITTED_GREEDY_MERGED_TRACKS_NAME = "RefittedMergedTracks"
REFITTED_GREEDY_MERGED_TRACKS_REL_NAME = "RefittedMergedTrackRelations"
CANDIDATE_AMBIGUOUS_MERGED_TRACKS_NAME = "CandidateAmbiguousMergedTracks"
REFITTED_AMBIGUOUS_MERGED_TRACKS_NAME = "RefittedAmbiguousMergedTracks"
REFITTED_AMBIGUOUS_MERGED_TRACKS_REL_NAME = "RefittedAmbiguousMergedTrackRelations"

# IO Paths
DEFAULT_DATA_DIR = Path.home() / "promotion" / "data"
DATA_DIR = Path(environ.get("dtDir", DEFAULT_DATA_DIR)) / "2026-04-13-tracking"
INPUT_FILE = DATA_DIR / "2026-04-13-fullreco-noECalGap-Clupatra-IF1_REC.edm4hep.root"
OUTPUT_FILE = DATA_DIR / "2026-04-try_track_merging.edm4hep.root"

# k4geo Paths
REL_PATH_2_DET_MOD_COMPACT = "FCCee/ILD_FCCee/compact/ILD_FCCee_v01/ILD_FCCee_v01.xml"
DEFAULT_K4GEO_DIR = Path.home() / "promotion" / "code" / "k4geo"
COMPACT_FILE_DET_MOD_PATH = (
    Path(environ.get("k4geo_DIR", DEFAULT_K4GEO_DIR)) / REL_PATH_2_DET_MOD_COMPACT
)

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
    geoSvc.detectors = [str(COMPACT_FILE_DET_MOD_PATH)]
    geoSvc.OutputLevel = INFO
    geoSvc.EnableGeant4Geo = False
    svcList.append(geoSvc)

    # iosvc.CollectionNames = [SI_TRACK_COLL_NAME, CLU_TRACK_COLL_NAME]

    MyFiller = CellIDEncodingFiller("CellIDEncodingFiller")
    MyFiller.CellIDEncodings = MISSING_ENCODINGS
    algList.append(MyFiller)

    ###########################################################
    # Start Track Variation Definitions
    ###########################################################

    TRACK_VARIATION_DEFS = {
        "Greedy": {
            "merge_name": CANDIDATE_GREEDY_MERGED_TRACKS_NAME,
            "refit_name": REFITTED_GREEDY_MERGED_TRACKS_NAME,
            "rel": REFITTED_GREEDY_MERGED_TRACKS_REL_NAME,
            "greedy": True,
        },
        "Ambiguous": {
            "merge_name": CANDIDATE_AMBIGUOUS_MERGED_TRACKS_NAME,
            "refit_name": REFITTED_AMBIGUOUS_MERGED_TRACKS_NAME,
            "rel": REFITTED_AMBIGUOUS_MERGED_TRACKS_REL_NAME,
            "greedy": False,
        },
    }

    ###########################################################
    # End Track Variation Definitions
    ###########################################################

    ###########################################################
    # Start Track Merging
    ###########################################################

    for track_type, col in TRACK_VARIATION_DEFS.items():
        merger = TrackMerger(
            f"{track_type}TrackMerger",
            InputSiTracks=SI_TRACK_COLL_NAME,
            InputCluTracks=CLU_TRACK_COLL_NAME,
            OutTracks=col["merge_name"],
            Greedy=col["greedy"],
        )
        merger.OutputLevel = DEBUG
        algList.append(merger)

    ###########################################################
    # End Track Merging
    ###########################################################

    ###########################################################
    # Start Refitting
    ###########################################################

    # MyRefitter = RefitFinal(
    #    "RefitFinal",
    #    InputTrackCollectionName=CANDIDATE_MERGED_TRACKS_NAME,
    #    InputRelationCollectionName=[],
    #    OutputTrackCollectionName=REFITTED_MERGED_TRACKS_NAME,
    # )

    SHARED_REFITTING_CONFIG = {
        "EnergyLossOn": ["true"],
        "FitDirection": ["+1"],
        "InitialTrackErrorD0": ["1e+06"],
        "InitialTrackErrorOmega": ["0.00001"],
        "InitialTrackErrorPhi0": ["100"],
        "InitialTrackErrorTanL": ["100"],
        "InitialTrackErrorZ0": ["1e+06"],
        "InitialTrackState": ["-1"],
        "TrackSystemName": ["DDKalTest"],
        "InputTrackRelCollection": [],
    }

    for track_type, col in TRACK_VARIATION_DEFS.items():
        refitter = MarlinProcessorWrapper(f"My{track_type}Refitter")
        refitter.ProcessorType = "RefitProcessor"
        refitter.Parameters = SHARED_REFITTING_CONFIG | {
            "InputTrackCollectionName": [col["merge_name"]],
            "OutputTrackCollectionName": [col["refit_name"]],
            "OutputTrackRelCollection": [col["rel"]],
        }
        refitter.OutputLevel = INFO
        algList.append(refitter)

    ###########################################################
    # End Refitting
    ###########################################################

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
