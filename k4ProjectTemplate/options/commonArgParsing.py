import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

# from g4units import rad

#####################################################################
# -- Usage Example --
# model = registry.get("FCC02")  # or "if2", or "ILD_FCCee_v02"
#####################################################################
parser_opt_use_long_det_name = "detname_long"
parser_opt_use_pub_det_name = "detname_pub"


@dataclass(frozen=True)
class HitCollection:
    root_tree_branch_name: str
    plot_collection_prefix: str


@dataclass(frozen=True)
class AcceleratorConfig:
    name: str
    relative_compact_file_dir: Path
    sim_crossing_angle_boost: float


@dataclass(frozen=True)
class DetectorModel:
    short_name: str  # e.g. 'v02'
    long_name: str  # e.g. 'FCC02'
    pub_name: str  # e.g. 'ILD_FCCee_v02'
    accelerator: AcceleratorConfig
    compact_path: Path
    sub_detector_collections: Dict[str, HitCollection]

    def get_compact_file_path(self) -> Path:
        return self.accelerator.relative_compact_file_dir / self.compact_path

    def get_crossing_angle(self) -> float:
        return self.accelerator.sim_crossing_angle_boost

    def is_accelerator(self, name: str) -> bool:
        return self.accelerator.name.lower() == name.lower()

    def get_name(self, args) -> str:
        if getattr(args, parser_opt_use_long_det_name, False):
            return self.long_name
        elif getattr(args, parser_opt_use_pub_det_name, False):
            return self.pub_name
        return self.short_name


class DetectorModelRegistry:
    def __init__(self):
        self._models: Dict[str, DetectorModel] = {}

    def register(self, model: DetectorModel):
        keys = {model.short_name, model.long_name, model.pub_name}
        for key in keys:
            self._models[key.lower()] = model

    def get(self, key: str) -> DetectorModel:
        return self._models[key.lower()]

    def list_keys(self) -> List[str]:
        # Return sorted short names (for argparse help etc.)
        return sorted(set(m.short_name for m in self._models.values()))

    def list_all_keys(self) -> List[str]:
        # Includes all name formats for validation or fuzzy matching
        return sorted(set(self._models.keys()))

    def __contains__(self, key: str) -> bool:
        return key.lower() in self._models


# -- Registry Setup --

FCC_dir = Path("FCCee") / "ILD_FCCee" / "compact"
ILC_dir = Path("ILD") / "compact" / "ILD_sl5_v02"

accelerators = {
    #    "FCCee": AcceleratorConfig("FCCee", FCC_dir, 15.0e-3 * rad),
    #    "ILC": AcceleratorConfig("ILC", ILC_dir, 7.0e-3 * rad),
    "FCCee": AcceleratorConfig("FCCee", FCC_dir, 15.0e-3),
    "ILC": AcceleratorConfig("ILC", ILC_dir, 7.0e-3),
}

sub_det_cols_fcc = {
    "vb": HitCollection("VertexBarrelCollection", "Vertex Barrel"),
    "ve": HitCollection("VertexEndcapCollection", "Vertex Endcap"),
}

sub_det_cols_ilc = {
    "vb": HitCollection("VXDCollection", "Vertex"),
    "f": HitCollection("FTDCollection", "Forward"),
}

registry = DetectorModelRegistry()

# Add models
registry.register(
    DetectorModel(
        "if1",
        "FCC01",
        "ILD_FCCee_v01",
        accelerators["FCCee"],
        Path("ILD_FCCee_v01/ILD_FCCee_v01.xml"),
        sub_det_cols_fcc,
    )
)
registry.register(
    DetectorModel(
        "if2",
        "FCC02",
        "ILD_FCCee_v02",
        accelerators["FCCee"],
        Path("ILD_FCCee_v02/ILD_FCCee_v02.xml"),
        sub_det_cols_fcc,
    )
)
registry.register(
    DetectorModel(
        "v02",
        "ILC02",
        "ILD_l5_v02",
        accelerators["ILC"],
        Path("ILD_l5_v02.xml"),
        sub_det_cols_ilc,
    )
)
registry.register(
    DetectorModel(
        "v03",
        "ILC03",
        "ILD_l5_v03",
        accelerators["ILC"],
        Path("ILD_l5_v03.xml"),
        sub_det_cols_ilc,
    )
)
registry.register(
    DetectorModel(
        "v05",
        "ILC05",
        "ILD_l5_v05",
        accelerators["ILC"],
        Path("ILD_l5_v05.xml"),
        sub_det_cols_ilc,
    )
)

# -- Argparse Integration --


def add_common_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--detectorModels",
        type=str,
        nargs="*",
        default=["v02"],
        choices=registry.list_keys() + [key.upper() for key in registry.list_keys()],
        help=f"Detector model(s) to use. Options: {', '.join(registry.list_keys())}",
    )
    parser.add_argument(
        "--version", type=str, required=True, help="Version tag for the run"
    )
    det_name_group = parser.add_mutually_exclusive_group()
    det_name_group.add_argument(
        "--" + parser_opt_use_long_det_name.replace('_',"-"),
        action="store_true",
        help="Use long name for detector models (e.g. ILC02)",
    )
    det_name_group.add_argument(
        "--" + parser_opt_use_pub_det_name.replace('_',"-"),
        action="store_true",
        help="Use publication name (longest) for detector models (e.g. ILD_FCCee_v02)",
    )
    return parser


# Case-insensitive short-name lookup (e.g. "V02" → "v02")
class CaseInsensitiveDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)


detModNames = CaseInsensitiveDict(
    {short_name: short_name for short_name in registry.list_keys()}
)
