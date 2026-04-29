import sys
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
CAND_COLL = tm.CANDIDATE_MERGED_TRACKS_NAME
REFT_COLL = tm.REFITTED_MERGED_TRACKS_NAME

from podio.root_io import Reader


def print_track_info(collection_name, tracks):
    """Prints track information in a formatted table with error handling for missing states."""
    if not tracks:
        print(f"\nCollection {collection_name} is empty.")
        return

    print(f"\n--- Collection: {collection_name} ({len(tracks)} tracks) ---")

    table_data = []
    headers = ["ID", "Chi2/NDF", "Hits", "D0", "Z0", "Phi", "Omega", "TanL"]

    for track in tracks:
        # Check if any track states exist before attempting to access index 0
        if track.trackStates_size() == 0:
            table_data.append(
                [
                    track.getObjectID().index,
                    f"{track.getChi2():.2f}/{track.getNdf()}",
                    track.trackerHits_size(),
                    "NO STATE",
                    "---",
                    "---",
                    "---",
                    "---",
                ]
            )
            continue

        state = track.getTrackStates(0)

        table_data.append(
            [
                track.getObjectID().index,
                f"{track.getChi2():.2f}/{track.getNdf()}",
                track.trackerHits_size(),
                f"{state.D0:.4f}",
                f"{state.Z0:.4f}",
                f"{state.phi:.4f}",
                f"{state.omega:.4e}",
                f"{state.tanLambda:.4f}",
            ]
        )

    print(tabulate(table_data, headers=headers, tablefmt="simple_outline"))


def main():
    if not Path(INPUT_FILE_2_ANA).exists():
        print(f"Error: Output file {INPUT_FILE_2_ANA} not found.")
        return

    reader = Reader(str(INPUT_FILE_2_ANA))
    events = reader.get("events")

    for i, event in enumerate(events):
        print(f"\n{'#' * 80}\n# Processing Event {i:3} \n{'#' * 80}")

        for coll_name in [CAND_COLL, REFT_COLL]:
            try:
                tracks = event.get(coll_name)
                print_track_info(coll_name, tracks)
            except KeyError:
                print(f"\n[!] Collection {coll_name} not found in event {i}")
            except Exception as e:
                print(f"\n[!] Unexpected error analyzing {coll_name}: {e}")


if __name__ == "__main__":
    main()
