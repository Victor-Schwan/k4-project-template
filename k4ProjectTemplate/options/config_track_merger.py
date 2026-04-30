from os import environ
from pathlib import Path

# ---------------------------------------------------------------------------
# Hot Fix: Missing CellID encodings
# ---------------------------------------------------------------------------

_ENCODING_STR = (
    "system:0:5,module:5:3,stave:8:4,tower:12:4,layer:16:6,"
    "wafer:22:6,slice:28:4,cellX:32:-16,cellY:48:-16"
)
MISSING_ENCODINGS = {
    key: _ENCODING_STR
    for key in [
        "EcalEndcapsCollectionGapHits",
        "EcalEndcapsCollection",
        "EcalEndcapsCollectionDigi",
        "EcalEndcapsCollectionRec",
        "EcalBarrelCollection",
        "EcalBarrelCollectionDigi",
        "EcalBarrelCollectionRec",
        "EcalBarrelCollectionGapHits",
        "EcalEndcapRingCollectionDigi",
        "EcalEndcapRingCollectionRec",
        "HcalBarrelCollectionDigi",
        "HcalBarrelCollectionRec",
        "HcalEndcapsCollectionDigi",
        "HcalEndcapsCollectionRec",
        "HcalEndcapRingCollectionDigi",
        "HcalEndcapRingCollectionRec",
        "LCAL",
        "MUON",
    ]
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_DEFAULT_DATA_DIR = Path.home() / "promotion" / "data"
_DATA_DIR = Path(environ.get("dtDir", _DEFAULT_DATA_DIR)) / "2026-04-13-tracking"

_DEFAULT_K4GEO_DIR = Path.home() / "promotion" / "code" / "k4geo"
_K4GEO_DIR = Path(environ.get("k4geo_DIR", _DEFAULT_K4GEO_DIR))
_REL_PATH_DETMOD = "FCCee/ILD_FCCee/compact/ILD_FCCee_v01/ILD_FCCee_v01.xml"

PATHS = {
    "input": _DATA_DIR / "2026-04-13-fullreco-IF1_REC.edm4hep.root",
    "output": _DATA_DIR / "2026-04-try_track_merging.edm4hep.root",
    "detmod_compact": _K4GEO_DIR / _REL_PATH_DETMOD,
}

# ---------------------------------------------------------------------------
# Track collection names
# ---------------------------------------------------------------------------

SI_TRACK_COLL_NAME = "SiTracksCT"
CLU_TRACK_COLL_NAME = "ClupatraTracks"
CLU_W_SI_TRACK_COLL_NAME = "MarlinTrkTracks"
MCP_COLL_NAME = "MCParticles"

# ---------------------------------------------------------------------------
# Track variations
# Each entry has:
#   "collections": input/output collection names
#   "merger":      merger-specific settings (None = no merger step)
#   "refitter":    refitter-specific settings
# ---------------------------------------------------------------------------

TRACK_VARIATIONS = {
    "Greedy": {
        "collections": {
            "merge_candidates": "CandidateGreedyMergedTracks",
            "refit_output": "RefittedGreedyMergedTracks",
            "refit_rel": "RefittedGreedyMergedTrackRelations",
        },
        "merger": {
            "enabled": True,
            "greedy": True,
        },
        "refitter": {
            "enabled": True,
        },
    },
    "Ambiguous": {
        "collections": {
            "merge_candidates": "CandidateAmbiguousMergedTracks",
            "refit_output": "RefittedAmbiguousMergedTracks",
            "refit_rel": "RefittedAmbiguousMergedTrackRelations",
        },
        "merger": {
            "enabled": True,
            "greedy": False,
        },
        "refitter": {
            "enabled": True,
        },
    },
    "CluWithSi": {
        "collections": {
            "merge_candidates": CLU_W_SI_TRACK_COLL_NAME,  # already exists, no merger
            "refit_output": "RefittedCluWithSiTracks",
            "refit_rel": "RefittedCluWithSiTrackRelations",
        },
        "merger": {
            "enabled": False,
        },
        "refitter": {
            "enabled": True,
        },
    },
}
