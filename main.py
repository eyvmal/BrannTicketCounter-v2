#!/usr/bin/env python3
from clubs.brann.brann import run_brann
from scrape_tools import get_time_formatted


def start_script():
    time_now = get_time_formatted("human")
    print("========================================")
    print(f"=  Running scripts,  {time_now}  =")
    print("========================================")


if __name__ == "__main__":
    '''
    TODO:
    * Fikse opp i typer, return-verdi og beskrivelser av alle funksjonene.
    * Error-håndtering
        '''
    start_script()
    run_brann("next", True, False)
