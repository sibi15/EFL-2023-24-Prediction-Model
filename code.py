import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.DataFrame()
teams = ["Barnsley","Birmingham City","Blackburn Rovers","Blackpool","Bournemouth","Brentford","Bristol City","Burnley",
"Cardiff City","Charlton Athletic","Coventry City","Derby County","Fulham","Huddersfield Town","Hull City","Ipswich Town",
"Leeds United","Leicester City","Luton Town","Middlesbrough","Millwall","Norwich City","Nottingham Forest",
"Peterborough United","Plymouth Argyle","Preston North End","Queens Park Rangers","Reading","Rotherham United",
"Sheffield Wednesday","Sheffield United","Stoke City","Southampton","Sunderland","Swansea City","Watford",
"West Bromwich Albion","Wigan Athletic","Wycombe Wanderers"]

for i in range(19,24):
    for team in teams:
        try:
            data = pd.concat([data, pd.read_excel("EFL_" + str(i) + "_" + str(i+1) + "/Team Stats " + 
                   team + ".xlsx")], ignore_index=True)
        except FileNotFoundError:
            pass
data = data[['Date','Match','Goals','Conceded goals','Possession, %','Duration']] 

fill_team = ""
start = 0
end = 0
data['Team'] = np.nan
for i in data['Date']:
    if i[0]=="2":
        end+=1
    else:
        data['Team'][start:end] = fill_team
        fill_team = i
        start=end
        end+=1
data['Team'][5225:] = data['Date'][5225]

data = data.dropna(axis=0)
data['Date'] = data['Date'].str.replace('-', '').astype(int)
data = data.reset_index(drop=True)
data['Goals'] = data['Goals'].astype(int)
data['Conceded goals'] = data['Conceded goals'].astype(int)

start = 0
data['Opponent Team'] = np.nan
data['H/A'] = np.nan
for i in data['Match']:
    temp = i[:-4].split(" - ")
    data['Opponent Team'][start:start+1] = np.where(temp[0]==data['Team'][start:start+1],temp[1].strip(),temp[0].strip())
    data['H/A'][start:start+1] = np.where(temp[0]==data['Team'][start:start+1],'H','A')
    start+=1
    
data['Opponent Possession'] = 100 - data['Possession, %']
data = data[['Date','Team','Opponent Team','H/A','Goals','Conceded goals','Possession, %','Opponent Possession','Duration']]
data = data.rename(columns={'Conceded goals':'Goals Conceded','Possession, %':'Possession'})

data_19_20 = data[(data.Date <= 20200722) & (data.Date >= 20190802)] #20200804 (10 knockout games)
data_20_21 = data[(data.Date <= 20210508) & (data.Date >= 20200911)] #20210529 (10 knockout games)
data_21_22 = data[(data.Date <= 20220507) & (data.Date >= 20210806)] #20220529 (10 knockout games)
data_22_23 = data[(data.Date <= 20230508) & (data.Date >= 20220729)] #20230527 (10 knockout games)
data_23_24 = data[(data.Date <= 20240122) & (data.Date >= 20230804)]

data_20_21 = data_20_21.append({'Date': 20200926, 'Team': "Birmingham City", 'Opponent Team': "Rotherham United",
                               'H/A':"H",'Goals':1,'Goals Conceded':1,'Possession':57.5,'Opponent Possession':42.5,
                               'Duration':95.0} , ignore_index = True)
data_20_21 = data_20_21.append({'Date': 20200926, 'Team': "Rotherham United", 'Opponent Team': "Birmingham City",
                               'H/A':"A",'Goals':1,'Goals Conceded':1,'Possession':42.5,'Opponent Possession':57.5,
                               'Duration':95.0} , ignore_index = True)
data_20_21 = data_20_21.sort_values(by=["Team","Date"], ascending=[True,False])
data_20_21.reset_index(drop=True, inplace=True)

seasons_data = [data_19_20,data_20_21,data_21_22,data_22_23,data_23_24]
seasons_tables = []

for season in seasons_data:
    season['PTs'] = np.where(season['Goals']>season['Goals Conceded'],3,np.where(season['Goals']==season['Goals Conceded'],1,0))
    season['W'] = np.where(season['PTs']==3,1,0)
    season['D'] = np.where(season['PTs']==1,1,0)
    season['L'] = np.where(season['PTs']==0,1,0)
    season['Goal Difference'] = season['Goals'] - season['Goals Conceded']
    season['Matches'] = 1
    season = season.groupby(['Team'])['Matches','W','D','L','Goals','Goals Conceded','Goal Difference','PTs'].sum().reset_index()
    season = season.rename(columns={'Matches':'MP','Goals':'GF','Goals Conceded':'GA','Goal Difference':'GD'})
    season.reset_index(drop=True, inplace=True)
    seasons_tables.append(season)
    
table_19_20 = seasons_tables[0]
table_20_21 = seasons_tables[1]
table_21_22 = seasons_tables[2]
table_22_23 = seasons_tables[3]
table_23_24 = seasons_tables[4]

table_19_20.loc[table_19_20['Team'] == 'Birmingham City', 'GA'] += 1
table_19_20.loc[table_19_20['Team'] == 'Birmingham City', 'GD'] -= 1
table_19_20.loc[table_19_20['Team'] == 'Hull City', 'GA'] += 1
table_19_20.loc[table_19_20['Team'] == 'Hull City', 'GD'] -= 1
table_19_20.loc[table_19_20['Team'] == 'Hull City', 'PTs'] -= 1
temp = table_19_20[['Team','PTs','GF','GD']]
temp = temp.rename(columns={'Team':'Team_Actual','PTs':'PTs_Actual'})
temp = temp.sort_values(by=["PTs_Actual", "GD","GF"], ascending=[False, False,False])
temp.reset_index(drop=True, inplace=True)
table_19_20.loc[table_19_20['Team'] == 'Wigan Athletic', 'PTs'] -= 12
table_19_20 = table_19_20.sort_values(by=["PTs", "GD","GF"], ascending=[False, False,False])
table_19_20.reset_index(drop=True, inplace=True)
table_19_20 = pd.concat([table_19_20, temp[['Team_Actual','PTs_Actual']]], axis=1)
table_19_20

table_20_21.loc[table_20_21['Team'] == 'Blackburn Rovers', 'GA'] += 1
table_20_21.loc[table_20_21['Team'] == 'Blackburn Rovers', 'GD'] -= 1
temp = table_20_21[['Team','PTs','GF','GD']]
temp = temp.rename(columns={'Team':'Team_Actual','PTs':'PTs_Actual'})
temp = temp.sort_values(by=["PTs_Actual", "GD","GF"], ascending=[False, False,False])
temp.reset_index(drop=True, inplace=True)
table_20_21.loc[table_20_21['Team'] == 'Sheffield Wednesday', 'PTs'] -= 6
table_20_21 = table_20_21.sort_values(by=["PTs", "GD","GF"], ascending=[False, False,False])
table_20_21.reset_index(drop=True, inplace=True)
table_20_21 = pd.concat([table_20_21, temp[['Team_Actual','PTs_Actual']]], axis=1)
table_20_21

temp = table_21_22[['Team','PTs','GF','GD']]
temp = temp.rename(columns={'Team':'Team_Actual','PTs':'PTs_Actual'})
temp = temp.sort_values(by=["PTs_Actual", "GD","GF"], ascending=[False, False,False])
temp.reset_index(drop=True, inplace=True)
table_21_22.loc[table_21_22['Team'] == 'Derby County', 'PTs'] -= 21
table_21_22 = table_21_22.sort_values(by=["PTs", "GD","GF"], ascending=[False, False,False])
table_21_22.reset_index(drop=True, inplace=True)
table_21_22 = pd.concat([table_21_22, temp[['Team_Actual','PTs_Actual']]], axis=1)
table_21_22

temp = table_22_23[['Team','PTs','GF','GD']]
temp = temp.rename(columns={'Team':'Team_Actual','PTs':'PTs_Actual'})
temp = temp.sort_values(by=["PTs_Actual", "GD","GF"], ascending=[False, False,False])
temp.reset_index(drop=True, inplace=True)
table_22_23.loc[table_22_23['Team'] == 'Reading', 'PTs'] -= 6
table_22_23.loc[table_22_23['Team'] == 'Wigan Athletic', 'PTs'] -= 6
table_22_23 = table_22_23.sort_values(by=["PTs", "GD","GF"], ascending=[False, False,False])
table_22_23.reset_index(drop=True, inplace=True)
table_22_23 = pd.concat([table_22_23, temp[['Team_Actual','PTs_Actual']]], axis=1)
table_22_23

table_23_24 = table_23_24.sort_values(by=["PTs", "GD","GF"], ascending=[False, False,False])
table_23_24.reset_index(drop=True, inplace=True)
table_23_24

tables = [table_19_20,table_20_21,table_21_22,table_22_23,table_23_24]
final_tables = []
for table in tables:
    table['Win_PC'] = table['W']/table['MP']
    table['Pyth_Exp'] = table['GF']**2/(table['GF']**2+table['GA']**2)
    final_tables.append(table)
table_19_20 = final_tables[0]
table_20_21 = final_tables[1]
table_21_22 = final_tables[2]
table_22_23 = final_tables[3]
table_23_24 = final_tables[4]

graphs = []
j = 2019
for i in final_tables:
    #graphs.append(sns.relplot(x="Pyth_Exp", y="Win_PC", data = i).set(title='Season '+str(j)+"_"+str((j+1)%100)))
    graphs.append(sns.relplot(x="Pyth_Exp", y="Win_PC", data = i).set(title='Season '+str(j)+"_"+str((j+1)%100)+" (Corr: " + str(i['Pyth_Exp'].corr(i['Win_PC'])) + ")"))
    j+=1
for i in graphs:
    plt.show()

regressions = []
for i in final_tables:
    regressions.append(smf.ols(formula = 'Win_PC ~ Pyth_Exp', data=i).fit())
j=2019
for i in regressions:
    print('\n\n\n\t\t\t\tSeason '+str(j)+"_"+str((j+1)%100)+"\n")
    print(i.summary())
    j+=1

data_half_1_23_24 = data[(data.Date <= 20231101) & (data.Date >= 20230804)]
data_half_2_23_24 = data[(data.Date <= 20240122) & (data.Date >= 20231102)]

data_half_1_23_24['PTs'] = np.where(data_half_1_23_24['Goals']>data_half_1_23_24['Goals Conceded'],3,np.where(data_half_1_23_24['Goals']==data_half_1_23_24['Goals Conceded'],1,0))
data_half_1_23_24['W'] = np.where(data_half_1_23_24['PTs']==3,1,0)
data_half_1_23_24['D'] = np.where(data_half_1_23_24['PTs']==1,1,0)
data_half_1_23_24['L'] = np.where(data_half_1_23_24['PTs']==0,1,0)
data_half_1_23_24['Matches'] = 1
data_half_1_23_24 = data_half_1_23_24.groupby(['Team'])['Matches','W','D','L','Goals','Goals Conceded','PTs'].sum().reset_index()
data_half_1_23_24 = data_half_1_23_24.rename(columns={'Matches':'MP1','W':'W1','D':'D1','L':'L1','Goals':'GF1','Goals Conceded':'GA1'})
data_half_1_23_24['Win_PC_1'] = data_half_1_23_24['W1']/data_half_1_23_24['MP1']
data_half_1_23_24['Pyth_Exp_1'] = data_half_1_23_24['GF1']**2/(data_half_1_23_24['GF1']**2 + data_half_1_23_24['GA1']**2)

data_half_2_23_24['PTs'] = np.where(data_half_2_23_24['Goals']>data_half_2_23_24['Goals Conceded'],3,np.where(data_half_2_23_24['Goals']==data_half_2_23_24['Goals Conceded'],1,0))
data_half_2_23_24['W'] = np.where(data_half_2_23_24['PTs']==3,1,0)
data_half_2_23_24['D'] = np.where(data_half_2_23_24['PTs']==1,1,0)
data_half_2_23_24['L'] = np.where(data_half_2_23_24['PTs']==0,1,0)
data_half_2_23_24['Matches'] = 1
data_half_2_23_24 = data_half_2_23_24.groupby(['Team'])['Matches','W','D','L','Goals','Goals Conceded','PTs'].sum().reset_index()
data_half_2_23_24 = data_half_2_23_24.rename(columns={'Matches':'MP2','W':'W2','D':'D2','L':'L2','Goals':'GF2','Goals Conceded':'GA2'})
data_half_2_23_24['Win_PC_2'] = data_half_2_23_24['W2']/data_half_2_23_24['MP2']
data_half_2_23_24['Pyth_Exp_2'] = data_half_2_23_24['GF2']**2/(data_half_2_23_24['GF2']**2 + data_half_2_23_24['GA2']**2)

predictor = pd.merge(data_half_1_23_24, data_half_2_23_24, on='Team')
pd.set_option('display.max_columns', None)

sns.relplot(x="Pyth_Exp_1", y="Win_PC_2", data = predictor).set(title='Correlation for Pyth_Exp_1 ~ Win_PC_2: ' + str(predictor['Pyth_Exp_1'].corr(predictor['Win_PC_2'])) + " for Season 2023/24")
sns.relplot(x="Win_PC_1", y="Win_PC_2", data = predictor).set(title='Correlation for Win_PC_1 ~ Win_PC_2: ' + str(predictor['Win_PC_1'].corr(predictor['Win_PC_2'])) + " for Season 2023/24")
plt.show()

keyvars = predictor[['Team','Win_PC_2','Win_PC_1','Pyth_Exp_1','Pyth_Exp_2']]
keyvars.corr()

prediction_23_24 = data[(data.Date <= 20240122) & (data.Date >= 20230804)]
prediction_23_24['PTs'] = np.where(prediction_23_24['Goals']>prediction_23_24['Goals Conceded'],3,np.where(prediction_23_24['Goals']==prediction_23_24['Goals Conceded'],1,0))
prediction_23_24['W'] = np.where(prediction_23_24['PTs']==3,1,0)
prediction_23_24['Matches'] = 1
prediction_23_24 = prediction_23_24.groupby(['Team'])['Matches','W','Goals','Goals Conceded','PTs'].sum().reset_index()
prediction_23_24 = prediction_23_24.rename(columns={'Matches':'MP','W':'W1','Goals':'GF','Goals Conceded':'GA'})
prediction_23_24['Pyth'] = prediction_23_24['GF']**2/(prediction_23_24['GF']**2 + prediction_23_24['GA']**2)
prediction_23_24['X_PTs'] = prediction_23_24['PTs'] + prediction_23_24['Pyth']*54
prediction_23_24['X_PTs'] = prediction_23_24['X_PTs'].astype(int)
prediction_23_24['MP'] = 46
prediction_23_24 = prediction_23_24[['Team','MP','X_PTs','Pyth']]
prediction_23_24.sort_values(by='X_PTs', ascending=False, inplace=True)
prediction_23_24.reset_index(drop=True,inplace=True)
prediction_23_24
