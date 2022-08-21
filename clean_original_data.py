import modin.pandas as pd 
from icecream import ic 


def main():
    table1 = pd.read_csv('title_akas.csv', dtype=str)
    table2 = pd.read_csv('title_basic.csv', dtype=str)
    table3 = pd.read_csv('title_rating.csv')

    region = table1[['titleId', 'title', 'region']].rename(columns={'titleId': 'id'})[['id', 'title', 'region']]
    region = region.replace(r'\N', 'unknown')

    detail = table2[['tconst', 'primaryTitle', 'runtimeMinutes', 'startYear', 'endYear', 'genres']]
    detail = detail.rename(columns={'tconst': 'id', 'runtimeMinutes': 'length', 'primaryTitle': 'title', 'startYear': 'start_year', 'endYear': 'end_year'})
    
    rating = table3.rename(columns={'tconst': 'id', 'averageRating': 'average_rating', 'numVotes': 'num_votes'})

    def format_id(value):
        return int(value.replace('tt', ''))

    detail['id'] = detail['id'].map(format_id)
    region['id'] = region['id'].map(format_id)
    rating['id'] = rating['id'].map(format_id)

    def format_detail(row_values, char_sets):
        row_values['start_year'] = ''.join(filter(str.isdigit, str(row_values['start_year'])))
        row_values['start_year'] = 0 if len(row_values['start_year']) == 0 else int(row_values['start_year'])
        
        row_values['end_year'] = ''.join(filter(str.isdigit, str(row_values['end_year'])))
        row_values['end_year'] = row_values['start_year'] if not row_values['end_year'].isdigit() else int(row_values['end_year'])
        
        row_values['length'] = ''.join(filter(str.isdigit, str(row_values['length']))) 
        row_values['length'] = 0 if not row_values['length'].isdigit() else int(row_values['length'])
        
        
        row_values['title'] = ''.join(filter(lambda char: char not in char_sets, str(row_values['title'])))
        
        row_values['genres'] = str(row_values['genres']).lower()
        return row_values 

    char_sets = set('!@#$%^&*()<>`~\'"+./;=?')
    detail = detail.apply(format_detail, axis=1, args=(char_sets, ))
    detail['start_year'] = detail['start_year'].astype(int)
    detail['end_year'] = detail['end_year'].astype(int)

    detail = detail.loc[detail['start_year'] >= 1950]
    detail = detail.loc[detail['length'] > 30]

    info = pd.merge(left=detail, right=rating, how='left', on=['id']).fillna(value=0)
    info['num_votes'] = info['num_votes'].astype(int)

    def filter_info(row_values):
        is_valid = 'episode' not in row_values['title'].lower() and 'pilot' not in row_values['title'].lower()
        is_valid = is_valid and row_values['average_rating'] >= 2 and row_values['num_votes'] >= 5
        return is_valid

    info = info.loc[info.apply(filter_info, axis=1)]

    genre_data = list(info['genres'].value_counts().to_dict().keys())
    genre_set = set()
    [genre_set.update(each.split(',')) for each in genre_data]
    genre_data = sorted(filter(lambda each: len(each) > 2, genre_set))

    def format_genre(value, genre_data):
        result = [0] * len(genre_data)
        for each in value['genres'].split(','):
            if each in genre_data:
                result[genre_data.index(each)] = 1 
        return result

    genre_table = info.apply(format_genre, axis=1, result_type='expand', args=(genre_data, ))
    genre_table.columns = genre_data

    agg_table = pd.concat([info, genre_table], axis=1).drop(columns=['genres'])

    agg_ids = set(agg_table['id'].value_counts().to_dict().keys())
    region = region.loc[region['id'].map(lambda each: each in agg_ids)]

    agg_table = agg_table.drop(columns=['id']).reset_index(drop=True).reset_index().rename(columns={'index':'id'})
    region = region.drop(columns=['id']).reset_index(drop=True)

    small_table = agg_table[['id', 'title']]
    region = pd.merge(left=region, right=small_table, on=['title'], how='inner').drop_duplicates(subset=['title', 'region'])
    region = region[['id', 'title', 'region']].sort_values(by=['id'])
    region = region.loc[region['region'] != 'unknown']

    ic(agg_table.dtypes)
    ic(region.dtypes)

    agg_table.to_csv('agg_table.csv', index=False)
    region.to_csv('region.csv', index=False)

if __name__ == '__main__':
    main() 


