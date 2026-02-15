import pandas as pd
import os

def generate_metadata():
    # Load raw data to get list of counties
    df = pd.read_csv('TJJD_-_County_Level_Referral_Data__FY_2013-2021.csv')
    counties = df['County'].unique()
    
    # Simple mapping logic for demo purposes (Texas Regions)
    # in a real scenario, we'd use a real lookup table/shapefile
    
    regions = {
        'HARRIS': 'Gulf Coast', 'DALLAS': 'Metroplex', 'TARRANT': 'Metroplex',
        'BEXAR': 'Alamo', 'TRAVIS': 'Capital', 'EL PASO': 'Upper Rio Grande',
        'COLLIN': 'Metroplex', 'DENTON': 'Metroplex', 'HIDALGO': 'South Texas',
        'FORT BEND': 'Gulf Coast', 'MONTGOMERY': 'Gulf Coast', 'WILLIAMSON': 'Capital',
        'CAMERON': 'South Texas', 'NUECES': 'Coastal Bend', 'BRAZORIA': 'Gulf Coast',
        'BELL': 'Central Texas', 'GALVESTON': 'Gulf Coast', 'LUBBOCK': 'High Plains',
        'WEBB': 'South Texas', 'JEFFERSON': 'South East Texas', 'MCLENNON': 'Central Texas',
        'SMITH': 'East Texas', 'BRAZOS': 'Central Texas', 'HAYS': 'Capital',
        'JOHNSON': 'Metroplex', 'ELLIS': 'Metroplex', 'ECTOR': 'Permian Basin',
        'MIDLAND': 'Permian Basin', 'GUADALUPE': 'Alamo', 'TAYLOR': 'West Texas',
        'WICHITA': 'North Texas', 'GREGG': 'East Texas', 'POTTER': 'High Plains',
        'GRAYSON': 'North Texas', 'RANDALL': 'High Plains', 'PARKER': 'Metroplex',
        'TOM GREEN': 'Concho Valley', 'COMAL': 'Alamo', 'KAUFMAN': 'Metroplex',
        'BOWIE': 'North East Texas', 'VICTORIA': 'Golden Crescent', 'HUNT': 'North Texas',
        'ROCKWALL': 'Metroplex', 'ORANGE': 'South East Texas', 'ANGELINA': 'Deep East Texas',
        'LIBERTY': 'Gulf Coast', 'HENDERSON': 'East Texas', 'TITUS': 'North East Texas',
        'WALKER': 'Gulf Coast', 'STARR': 'South Texas'
    }
    
    def get_region(county):
        if county in regions:
            return regions[county]
        # Fallback based on first letter for "random" but deterministic distribution in demo
        if county[0] in ['A', 'B', 'C']: return 'North Texas'
        if county[0] in ['D', 'E', 'F']: return 'East Texas'
        if county[0] in ['G', 'H', 'I']: return 'Central Texas'
        if county[0] in ['J', 'K', 'L', 'M']: return 'West Texas'
        return 'South Texas'

    metadata_data = []
    for county in counties:
        metadata_data.append({
            'County': county,
            'Region': get_region(county),
            'State': 'TX'
        })
        
    meta_df = pd.DataFrame(metadata_data)
    
    os.makedirs('data', exist_ok=True)
    meta_df.to_csv('data/County_Metadata.csv', index=False)
    print(f"Generated data/County_Metadata.csv with {len(meta_df)} counties.")

if __name__ == "__main__":
    generate_metadata()
