import argparse, logging

from core import *

def main():
    parser = argparse.ArgumentParser(description="Fetch questions for a given year and pages.")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year to fetch data for.")
    parser.add_argument('-p', '--page', type=int, required=True, help="Page number to start from.")

    args = parser.parse_args()

    year = args.year
    page = args.page

    access_token = get_token()

    intervals = fullyear(year)

    for interval in intervals:
        # questions = fetch_questions_for_month(access_token=access_token, start_date=interval['start_date'], end_date=interval['end_date'], page)
        save_questions([])
        
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f'Um erro ocorreu: {str(e)}', level=logging.ERROR)
