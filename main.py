import argparse, logging

from core import *

def main():
    parser = argparse.ArgumentParser(description="Fetch questions for a given year and pages.")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year to fetch data for.")
    parser.add_argument('-p', '--page', type=int, required=True, help="Page number to start from.")
    parser.add_argument('-m', '--multithread', type=bool, required=False, default=False, 
                        action=argparse.BooleanOptionalAction, help='Activates multithreading (prototype)')
    parser.add_argument('-e', '--exclude', type=str, required=False, help='Month(s) to exclude')

    args = parser.parse_args()

    year = args.year
    page = args.page
    multithread = args.multithread
    exclude = args.exclude

    access_token = get_token()

    intervals = fullyear(year)

    if multithread:
        multithreading(access_token, intervals, page, exclude)
    else:
        sequential(access_token, intervals, page, exclude)
        
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f'Um erro ocorreu: {str(e)}', level=logging.ERROR)
