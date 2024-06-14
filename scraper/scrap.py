# Don't Add All data at once Enter Manual Year and Round Values to not get Server Timeouts 
from bs4 import BeautifulSoup
import mechanize 
import pandas as pd
def get_jitems(browser,element):
    brwsr.select_form(nr = 0)
    ctl = browser.form.find_control(element)
    state_items = ctl.get_items()
    return state_items[1:] 
 
brwsr = mechanize.Browser()
header=['Institute','Academic Program Name','Quota','Seat Type','Gender','Opening Rank','Closing Rank','Year','Round']
df = pd.DataFrame(columns = header)
brwsr.open('https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx')
for year in get_jitems(brwsr,'ctl00$ContentPlaceHolder1$ddlYear'):
    print(year)
    brwsr.select_form(nr = 0)
    brwsr['ctl00$ContentPlaceHolder1$ddlYear'] = [str(year)]
    response = brwsr.submit()
    for round in get_jitems(brwsr,'ctl00$ContentPlaceHolder1$ddlroundno'):
        brwsr.select_form(nr = 0)
        brwsr['ctl00$ContentPlaceHolder1$ddlroundno'] = [str(round),]
        response = brwsr.submit()
        brwsr.select_form(nr = 0)
        brwsr['ctl00$ContentPlaceHolder1$ddlInstype'] = ['ALL']
        response = brwsr.submit()
        brwsr.select_form(nr = 0)
        brwsr['ctl00$ContentPlaceHolder1$ddlInstitute'] = ['ALL']
        response = brwsr.submit()
        brwsr.select_form(nr = 0)
        brwsr['ctl00$ContentPlaceHolder1$ddlBranch'] = ['ALL']
        response = brwsr.submit()
        brwsr.select_form(nr = 0)
        brwsr['ctl00$ContentPlaceHolder1$ddlSeatType'] = ['ALL']
        response = brwsr.submit()
        soup=BeautifulSoup(response.read(),'lxml')
        table = soup.table

        for i in table.find_all('tr')[1:]:
            row_data = i.find_all('td')
            row = []
            if row_data[1].span:
                row.append(row_data[0].text)
                for j in row_data[1:]:
                    row.append(j.span.text)
                row.append(str(year))
                row.append(str(round))
                df = df._append(pd.Series(row, index=df.columns[:len(row)]), ignore_index=True)
                df.to_csv('jossa2.csv')

