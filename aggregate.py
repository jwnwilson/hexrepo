import argparse
from typing import Literal

parser = argparse.ArgumentParser(description="run aggregate")
parser.add_argument("--aggregate", type=str)
parser.add_argument("--port", type=int)
parser.add_argument('integers', metavar='N', type=int, nargs='+',
                help='an integer for the accumulator')
args = parser.parse_args()



def run_aggregate(aggregate: Literal["sum", "max"], integers: list[int]) -> int:
    func: dict[str, callable] = {
            "sum": sum,
            "max": max
    }
    if args.aggregate in func:
        return (func[args.aggregate](args.integers))
    else:
        raise ValueError("unknown aggregate function")
    

def run_server(port: int):
    pass

if __name__ == "__main__":
    breakpoint()
    if args.port:
        print("not implemented")
    else:
        print(run_aggregate(args.aggregate, args.integers))