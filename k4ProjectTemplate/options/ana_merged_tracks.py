import sys
from itertools import zip_longest
from math import sqrt
from pathlib import Path
from unittest.mock import MagicMock

from tabulate import tabulate

# 1. Mock 'Configurables' BEFORE importing trackMerger
# This prevents the ImportError because it gives trackMerger a "fake"
# object to import from.
mock_configurables = MagicMock()
sys.modules["Configurables"] = mock_configurables

# 2. Ensure the directory is in sys.path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# 3. Now import your steering file safely
try:
    import track_merger as tm

    print(f"Successfully loaded SSOT variables from: {tm.__file__}")
except ImportError as e:
    print(f"Failed to import trackMerger: {e}")
    sys.exit(1)

# Now you can use your variables
INPUT_FILE_2_ANA = tm.OUTPUT_FILE
CAND_COLL = tm.CANDIDATE_GREEDY_MERGED_TRACKS_NAME
REFT_COLL = tm.REFITTED_GREEDY_MERGED_TRACKS_NAME
SI_COLL = tm.SI_TRACK_COLL_NAME
CLU_COLL = tm.CLU_TRACK_COLL_NAME
CLU_W_SI_COLL = tm.CLU_W_SI_TRACKS_NAME
MCP_COLL = "MCParticles"

from podio.root_io import Reader


def main():
    if not Path(INPUT_FILE_2_ANA).exists():
        print(f"Error: Output file {INPUT_FILE_2_ANA} not found.")
        return

    events = Reader(str(INPUT_FILE_2_ANA)).get("events")

    # List of collections to compare
    coll_names = [MCP_COLL, REFT_COLL, SI_COLL, CLU_W_SI_COLL, CLU_COLL, CAND_COLL]

    for i, event in enumerate(events):
        print(f"\n{'#' * 80}\n# Processing Event {i:3} \n{'#' * 80}")

        # Retrieve all collections for this event
        collections_data = []
        for name in coll_names:
            try:
                collections_data.append(event.get(name))
            except KeyError:
                print(f"[!] Warning: Collection {name} missing in event {i}")

        # check if lengths are inconsistent
        lengths = [len(c) if c is not None else 0 for c in collections_data]
        if len(set(lengths)) > 1:
            print(
                "Note: Collections have different sizes: "
                + ", ".join([f"{n}: {l}" for n, l in zip(coll_names, lengths)])
            )

        table_data = []
        headers = ["Coll", "ID", "Chi2/NDF", "Hits", "D0", "Z0", "Phi", "Omega", "TanL"]

        # Use zip_longest to iterate over all collections at once
        # i-th row contains the i-th track from each collection
        for i, tracks_group in enumerate(
            zip_longest(*collections_data, fillvalue=None)
        ):
            if i > 0:
                # Add a separator line between groups of i-th tracks for clarity
                table_data.append(["~" * 5] * len(headers))
            for idx, track in enumerate(tracks_group):
                coll_label = coll_names[idx]

                if track is None:
                    # Fill row with '-' if the collection is shorter than others
                    table_data.append([coll_label] + ["-"] * (len(headers) - 1))
                    continue

                if coll_label == MCP_COLL:
                    if track.getGeneratorStatus() != 1:
                        # Only analyze stable particles (status=1)
                        continue
                    # For muons from a gun, we look at the primary particle (index 0)

                    # Example conversion logic (Simplified for Muon Gun at IP)
                    # In a real study, you'd calculate D0/Z0 based on track.getVertex()
                    p_t = sqrt(track.getMomentum().x ** 2 + track.getMomentum().y ** 2)
                    a = 3e-4  # GeV/c per Tesla, for charge=1
                    B_z = 2.0  # Tesla, example magnetic field strength
                    table_data.append(
                        [
                            coll_label,
                            track.getObjectID().index,
                            "---",
                            "---",
                            f"{sqrt(track.getVertex().x ** 2 + track.getVertex().y ** 2):.2f}",  # Placeholders for comparison
                            f"{track.getVertex().z:.2f}",
                            "---",
                            f"|{a * B_z / p_t:.4e}|",  # abs(Omega) ~ a*B_z/pT
                            # f"{track.getPhi():.4f}",
                            # f"p:{track.getMomentum().x:.1f}",  # Or calculate Omega
                            f"{track.getMomentum().z / p_t:.4f}",
                        ]
                    )
                    continue

                # Process Track Info
                ndf = track.getNdf()
                chi2_str = f"{track.getChi2():.2f}/{ndf}"
                if ndf > 0:
                    chi2_str += f"={track.getChi2() / ndf:.2f}"

                if track.trackStates_size() == 0:
                    table_data.append(
                        [
                            coll_label,
                            track.getObjectID().index,
                            chi2_str,
                            track.trackerHits_size(),
                            "NO STATE",
                            "---",
                            "---",
                            "---",
                            "---",
                        ]
                    )
                else:
                    state = track.getTrackStates(0)
                    table_data.append(
                        [
                            coll_label,
                            track.getObjectID().index,
                            chi2_str,
                            track.trackerHits_size(),
                            f"{state.D0:.4f}",
                            f"{state.Z0:.4f}",
                            f"{state.phi:.4f}",
                            f"{state.omega:.4e}",
                            f"{state.tanLambda:.4f}",
                        ]
                    )

        print(tabulate(table_data, headers=headers, tablefmt="simple_outline"))


if __name__ == "__main__":
    main()
