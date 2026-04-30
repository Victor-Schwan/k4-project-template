import sys
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config_track_merger import (
    CLU_TRACK_COLL_NAME,
    MISSING_ENCODINGS,
    PATHS,
    SI_TRACK_COLL_NAME,
    TRACK_VARIATIONS,
)


def main():
    svcList = []
    algList = []

    iosvc = IOSvc()
    iosvc.Input = str(PATHS["input"])
    iosvc.Output = str(PATHS["output"])
    svcList.append(iosvc)

    io_handler = IOHandlerHelper(algList, iosvc)
    io_handler.add_reader([str(PATHS["input"])])
    io_handler.add_edm4hep_writer(str(PATHS["output"]))

    geoSvc = GeoSvc("GeoSvc")
    geoSvc.detectors = [str(PATHS["detmod_compact"])]
    geoSvc.OutputLevel = INFO
    geoSvc.EnableGeant4Geo = False
    svcList.append(geoSvc)

    MyFiller = CellIDEncodingFiller("CellIDEncodingFiller")
    MyFiller.CellIDEncodings = MISSING_ENCODINGS
    algList.append(MyFiller)

    # ------------------------------------------------------------------
    # Track Merging
    # ------------------------------------------------------------------

    for track_type, var in TRACK_VARIATIONS.items():
        if not var["merger"]["enabled"]:
            continue
        colls = var["collections"]
        merger = TrackMerger(
            f"{track_type}TrackMerger",
            InputSiTracks=SI_TRACK_COLL_NAME,
            InputCluTracks=CLU_TRACK_COLL_NAME,
            OutTracks=colls["merge_candidates"],
            Greedy=var["merger"]["greedy"],
        )
        merger.OutputLevel = DEBUG
        algList.append(merger)

    # ------------------------------------------------------------------
    # Refitting
    # ------------------------------------------------------------------

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

    for track_type, var in TRACK_VARIATIONS.items():
        if not var["refitter"]["enabled"]:
            continue
        colls = var["collections"]
        refitter = MarlinProcessorWrapper(f"{track_type}Refitter")
        refitter.ProcessorType = "RefitProcessor"
        refitter.Parameters = SHARED_REFITTING_CONFIG | {
            "InputTrackCollectionName": [colls["merge_candidates"]],
            "OutputTrackCollectionName": [colls["refit_output"]],
            "OutputTrackRelCollection": [colls["refit_rel"]],
        }
        refitter.OutputLevel = INFO
        algList.append(refitter)

    # ------------------------------------------------------------------

    io_handler.finalize_converters()

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


main()
