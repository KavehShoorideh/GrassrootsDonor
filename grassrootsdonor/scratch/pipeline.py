# functions to run the data pipeline
import pandas as pd
from datetime import datetime
from collections import defaultdict

from grassrootsdonor import helper

import grassrootsdonor.config as cfg


def clean_data(votes_files, money_files):
    print('Cleaning!')

    from fuzzywuzzy import fuzz
    # THIS LINE DISABLES CHAINED ASSIGNMENT WARNING WHICH POPS UP WHEN APPLYING FIXDATES
    pd.options.mode.chained_assignment = None
    df_money = pd.concat((pd.read_csv(f, low_memory=False, encoding='iso-8859-1') for f in cfg.money_files))
    print(f'Sucessfully loaded {[str(f) for f in money_files]}')
    df_votes = pd.concat((pd.read_excel(f, encoding='iso-8859-1') for f in cfg.votes_files))
    print(f'Sucessfully loaded {[str(f) for f in votes_files]}')

    # Fix dates
    df_money.loc[:, 'TransactionDate'] = df_money['TransactionDate'].apply(helper.fixDates)
    df_votes.loc[:, 'ELECTION_DATE'] = df_votes['ELECTION_DATE'].apply(helper.fixDates)
    df_money.loc[:, 'Election'] = df_money['Election'].apply(helper.fixDates)
    # Fix names
    df_money.loc[:, 'RecipientCandidateNameNormalized'] = df_money['RecipientCandidateNameNormalized'].str.upper()
    df_votes.loc[:, 'CANDIDATE_NAME'] = df_votes['CANDIDATE_NAME'].str.upper()
    df_money.loc[:, 'RecipientCandidateNameNormalized'] = df_money.loc[:, 'RecipientCandidateNameNormalized'].apply(
        helper.fixName)


    # Create name mapping and apply to match tables on name
    names_money = list(df_money['RecipientCandidateNameNormalized'].unique())
    names_votes = list(df_votes['CANDIDATE_NAME'].unique())
    name_mapping = {}
    for x in names_money:
        for y in names_votes:
            match = False
            result = fuzz.token_set_ratio(x, y)
            if result > 80:
                match = True
                name_mapping[x] = y
                break

    df_money.loc[:, 'RecipientCandidateNameNormalized'] = df_money.RecipientCandidateNameNormalized.map(name_mapping)

    # Calculate outcome
    df_votes = helper.findPrimaryOutcome(df_votes)
    df_money = df_money.apply(helper.imputeZeroDates, axis=1)

    # df_money.to_csv(cfg.dataDir / '_temp_cleaned_money.csv')
    # df_votes.to_csv(cfg.dataDir / '_temp_cleaned_votes.csv')
    engineerFeatures(df_votes, df_money)

def engineerFeatures(dfVotes, dfMoney, today=datetime.today()):
    #
    # dfMoney = pd.read_csv(cfg.dataDir / '_temp_cleaned_money.csv')
    # dfVotes = pd.read_csv(cfg.dataDir / '_temp_cleaned_votes.csv')

    # Create candidate table
    print('Engineering!')

    candTable = dfVotes['CANDIDATE_NAME'].drop_duplicates().reset_index(drop=True).reset_index().rename(
        columns={'index': 'cid'})
    candColumns = ['ELECTION_DATE', 'CONTEST_NAME', 'CANDIDATE_NAME', 'PARTY_NAME', 'PARTY_ID', 'OUTCOME', 'VOTE_TOTAL',
                   'INCUMBENT_FLAG', 'WRITE_IN_FLAG']
    dfCand = dfVotes[candColumns].drop_duplicates()

    # Merge the cid back in
    dfCand = pd.merge(dfCand, candTable, left_on='CANDIDATE_NAME', right_on='CANDIDATE_NAME')

    # race table:
    raceColumns = ['ELECTION_DATE', 'CONTEST_NAME']
    dfRace = dfVotes[raceColumns].drop_duplicates()
    dfRace = dfRace.reset_index(drop=True).reset_index().rename(columns={'index': 'rid'})
    dfRace.CONTEST_NAME.value_counts().value_counts()

    # merge rid back into candidate table
    dfCand = pd.merge(dfCand,
                      dfRace,
                      left_on=['ELECTION_DATE', 'CONTEST_NAME'],
                      right_on=['ELECTION_DATE', 'CONTEST_NAME'], how='inner')
    # dfCand.drop(['ELECTION_DATE', 'CONTEST_NAME'], axis=1, inplace=True)

    # map party names to values
    partyMap = defaultdict(lambda: 0)
    partyMap['Democratic'] = -1
    partyMap['Green'] = -1
    partyMap['American Independent'] = 1
    partyMap['Republican'] = 1

    dfCand['PARTY_LEAN'] = dfCand['PARTY_NAME'].map(partyMap)

    # Mark races that have 2 or less praticipants
    dfRace['NO_CONTEST'] = dfRace.rid.apply(lambda x: 0 if len(dfCand[dfCand.rid == x]) > 2 else 1)
    # Keep only state senate and assembly races
    dfRace['LEGISLATURE'] = dfRace.CONTEST_NAME.str.contains(r'(State Assembly)|(State Senate)', na=True)
    dfRace = dfRace[(dfRace.LEGISLATURE == 1) & (dfRace.NO_CONTEST == 0)]

    # Remerge to get rid of no_contest races or non legislature races
    dfCand = pd.merge(dfCand,
                      dfRace,
                      left_on=['ELECTION_DATE', 'rid', 'CONTEST_NAME'],
                      right_on=['ELECTION_DATE', 'rid', 'CONTEST_NAME'], how='inner')

    # Merge race id into money data
    dfMoney = pd.merge(dfMoney, dfCand, left_on=['Election', 'RecipientCandidateNameNormalized'],
                       right_on=['ELECTION_DATE', 'CANDIDATE_NAME'], how='inner')

    # encode incumbent flag
    dfCand['INCUMBENT_FLAG'] = dfCand.INCUMBENT_FLAG.replace({'Y': 1, 'N': 0})

    dfMoney.to_csv(cfg.training_money_file)
    dfRace.to_csv(cfg.training_race_file)
    dfCand.to_csv(cfg.training_candidate_file)

