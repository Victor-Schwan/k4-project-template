# argparse
detModOpts = ["v02", "if1", "if2"]


class CaseInsensitiveDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)


detModNames = CaseInsensitiveDict({el: el for el in detModOpts})


def addCommonArgs(parser):
    parser.add_argument(
        "--detectorModels",
        "-m",
        help="Which detector model(s) to run reconstruction for",
        choices=detModOpts + [el.upper() for el in detModOpts],
        type=str,
        default=["V02"],
        nargs="*",
    )
    parser.add_argument(
        "--version",
        type=str,
        help="str to identify a run through the pipeline",
        required=True,
    )
    return parser
