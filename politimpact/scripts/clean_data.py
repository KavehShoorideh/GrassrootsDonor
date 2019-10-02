
def clean_data(votes_files, money_files):
    print('Cleaning!')
    from fuzzywuzzy import fuzz
    race_key = ['CONTEST_NAME', 'ELECTION_DATE']
    cand_key = ['CANDIDATE_NAME', 'CONTEST_NAME', 'ELECTION_DATE']


    dfMoney = pd.concat((pd.read_csv(f, low_memory=False, encoding='iso-8859-1') for f in cfg.money_files))
    print(f'Sucessfully loaded {[str(f) for f in money_files]}')
    dfVotes = pd.concat((pd.read_excel(f, encoding='iso-8859-1') for f in cfg.votes_files))
    print(f'Sucessfully loaded {[str(f) for f in votes_files]}')

    # Keep only county totals in votes
    # THIS LINE DISABLES CHAINED ASSIGNMENT WARNING WHICH POPS UP WHEN ASSIGNING using .loc
    pd.options.mode.chained_assignment = None
    dfVotes = dfVotes[dfVotes['COUNTY_NAME'] == 'State Totals']
    dfVotes.loc[:, 'ELECTION_DATE'] = pd.to_datetime(dfVotes['ELECTION_DATE'], errors='coerce')
    dfVotes.dropna(subset=['ELECTION_DATE'], inplace=True)
    dfVotes.loc[:, 'CANDIDATE_NAME'] = dfVotes['CANDIDATE_NAME'].str.upper()

    def imputeZeroDates(row):
        """ impute 0000-00-00 in date columns"""
        x = row['Election']
        y = row['ElectionCycle']
        if pd.isnull(x) and not pd.isnull(y):
            row['Election'] = nextElection(fixDates(str(y)), electionDates)
        return row

    # Fix zero dates
    dfMoney = dfMoney.apply(imputeZeroDates, axis=1)

    # # Fix dates
    # dfMoney.loc[:, 'TransactionDate'] = dfMoney['TransactionDate'].apply(helper.fixDates)
    # dfMoney.loc[:, 'Election'] = dfMoney['Election'].apply(helper.fixDates)
    # # Fix names
    # dfMoney.loc[:, 'RecipientCandidateNameNormalized'] = dfMoney['RecipientCandidateNameNormalized'].str.upper()
    # dfMoney.loc[:, 'RecipientCandidateNameNormalized'] = dfMoney.loc[:, 'RecipientCandidateNameNormalized'].apply(
    #     helper.fixName)

    dfMoney.loc[:, 'TransactionDate'] = pd.to_datetime(dfMoney['TransactionDate'], errors='coerce')
    dfMoney.loc[:, 'Election'] = pd.to_datetime(dfMoney['Election'], errors='coerce')
    dfMoney.dropna(subset=['Election','TransactionDate'], inplace=True)
    # Fix names
    dfMoney.loc[:, 'RecipientCandidateNameNormalized'] = dfMoney['RecipientCandidateNameNormalized'].str.upper()
    dfMoney.loc[:, 'RecipientCandidateNameNormalized'] = dfMoney.loc[:, 'RecipientCandidateNameNormalized'].apply(
        helper.fixName)

    # Create name mapping and apply to match tables on name
    names_money = list(dfMoney['RecipientCandidateNameNormalized'].unique())
    names_votes = list(dfVotes['CANDIDATE_NAME'].unique())
    name_mapping = {}
    for x in names_money:
        for y in names_votes:
            match = False
            result = fuzz.token_set_ratio(x, y)
            # 80 seemed to work well and matches are near perfect
            if result > 80:
                match = True
                name_mapping[x] = y
                break
    dfMoney.loc[:, 'RecipientCandidateNameNormalized'] = dfMoney.RecipientCandidateNameNormalized.map(name_mapping)

    # Convert to tables
    columns = [*cand_key, 'PARTY_NAME', 'INCUMBENT_FLAG', 'WRITE_IN_FLAG', 'VOTE_TOTAL']
    dfCand = dfVotes[columns].drop_duplicates()
    # race table:
    dfRace = dfVotes[race_key].drop_duplicates()
    # Merge race id into money data
    dfMoney = dfMoney.rename(
        columns={
            'Election': 'ELECTION_DATE',
            'TransactionAmount': 'TRANSACTION_AMOUNT',
            'TransactionDate': 'TRANSACTION_DATE',
            'RecipientCandidateNameNormalized': 'CANDIDATE_NAME',
            'RecipientCommitteeNameNormalized': 'COMMITTEE_NAME',
            'DonorNameNormalized' : 'DONOR_NAME',
            'DonorZipCode': 'DONOR_ZIP',
            'DonorEntityType': 'DONOR_ENTITY_TYPE',  # PTY, IND, OTH, SCC
            'DonorOrganization': 'DONOR_ORG',
            'RecipientCandidateOffice': 'OFFICE',
            'RecipientCandidateDistrict': 'DISTRICT'
        })

    # Used inner join to exclude any candidate for whom there is no money info or no vote info
    # But maybe right join is right?
    dfMoney = pd.merge(dfMoney, dfCand, left_on=['CANDIDATE_NAME', 'ELECTION_DATE'],
                       right_on=['CANDIDATE_NAME', 'ELECTION_DATE'], how='right')
    dfMoney.dropna(subset=['CANDIDATE_NAME'])
    dfMoney[['TRANSACTION_AMOUNT']] = dfMoney[['TRANSACTION_AMOUNT']].fillna(value=0)

    # Calculate outcome
    # dfVotes = helper.findPrimaryOutcome(dfVotes)

    # Save files
    dfMoney.to_csv(cfg.cleaned_money_file)
    dfRace.to_csv(cfg.cleaned_race_file)
    dfCand.to_csv(cfg.cleaned_candidate_file)
    return (dfCand, dfRace, dfMoney)


if __name__ == '__main__':
    tables = clean_data(cfg.votes_files, cfg.money_files)
    print('Done!')
