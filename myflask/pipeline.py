# functions to run the data pipeline

def launch_pipeline(user_fav_cand, user_budget, user_zip_code):


    temp_output = [dict(index=1, candidate=user_fav_cand,
                               win_chance_before='10%', win_chance_after='100%', web_link="https://www.google.com/")]
    return temp_output

