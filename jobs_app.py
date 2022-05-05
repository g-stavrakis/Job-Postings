import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from PIL import Image

import base64

from IPython.display import HTML
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

###################### Creating the Functions for the app ##########################

## Creating the function for Scraping the Job listings

def scrape(role,place, jobtype):
    
    # Creating the Link 
    role = role.replace(' ', '%20')

    base_url = 'https://uk.indeed.com/jobs?q='

    url_page = base_url + role + '&l=' + place + '&jt=' + jobtype +'&start='
    
    url_posting = base_url + role + '&l=' + place + '&vjk='


    # Scrape the pages:
    for j in range(10,70,10):  # make 400 at the end

        #Creating the new link
        url = url_page+str(j)

        # Make the request for the html file
        response = requests.get(url)

        # Parse the html file using BeautifulSoup
        soup = BeautifulSoup(response.content,"html.parser")

        # Initialization of the lists:
        Job_Titles, Companies, Locations, Salaries, Short_Description, Date_Posted, Job_Link = [],[],[],[],[],[],[]

        # Taking all the listings for the page
        lists = soup.find_all('table', class_ = 'jobCard_mainContent')
        table2 = soup.find_all('table', class_ = 'jobCardShelfContainer')

        for i in range(len(lists)):

            # For title 
            title = lists[i].find('h2').text
            if title[:3] == 'new':
                title = title[3:]
            Job_Titles.append(title)

            # For company name
            company = lists[i].find('span',class_ ="companyName").text
            Companies.append(company)

            # Company's location
            location = lists[i].find('div',class_ ="companyLocation").text
            Locations.append(location)

            # Company's salary
            try:
                salary = lists[i].find('div',class_ ="salary-snippet").text
            except:
                salary = '-'
            Salaries.append(salary)

            # Job's short description
            short_description = table2[i].find('div', class_ = 'job-snippet').text
            if short_description[:1] == '\n' :
                short_description = short_description[1:-1]
            Short_Description.append(short_description)

            # Job posting date
            date = table2[i].find('span', class_ = 'date').text
            if date[:6] == 'Posted':
                date = date[6:]
            Date_Posted.append(date)

            # Links for positions
            link = table2[i].find_all('a')[2].get('href')
            link = url_posting + link.split('&')[1].split('=')[1]
            Job_Link.append(link)

        Posting_Data_Page = pd.DataFrame({'Job_Titles':Job_Titles,'Companies': Companies,'Locations': Locations,
                                     'Salaries': Salaries,'Short_Description':Short_Description,
                                     'Date_Posted': Date_Posted, 'Job_Link': Job_Link})
        

        if j==10:
            Posting_Data = Posting_Data_Page
        else:
            Posting_Data = pd.concat([Posting_Data, Posting_Data_Page], ignore_index=True)
            
    return Posting_Data


## Creating the function for Job screening

def job_screening(data):
    
    # Loading the companies that provide visa
    companies = pd.read_csv('Companies.csv')
    
    # Finding the Jobs of the companies that appeared in the list --> assumption (Companies name contained )
    result = [i for i in range(len(data))
          if any(companies['Organisation Name'].str.contains(data.iloc[i]['Companies']))]
    
    # Creating the new Dataframe
    output = data.iloc[result]
    
    return output

# Creating fuction to download the csv with the listings 

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Visa_Job_Postings-Good_Luck.csv">Download CSV File</a>'
    return href

# Creating fuction to

def make_clickable(link):
    # target _blank to open new window
    return f'<a target="_blank" href="{link}">See_Posting</a>'

# Creating the fuction for the animation

def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

########################## Creating the web application ##########################

# Setting up the configuration of the page

st.set_page_config(page_title='Job Seeker', page_icon=':tada:', layout='wide')

# Creating a navigation bar

selected = option_menu(None,
                       ["Home", 'Visa Providers','About Me'], 
        icons=['house', 'award','person-circle'], menu_icon="cast", default_index=0,
                       orientation = 'horizontal')

### Creating the first tab
if selected == 'Home':

    # The title of the Page

    st.write("""

    # Vaccancies for Visa providers

    Here you can search for Job posting only for companies that are eligible to provide visa to their candidates.


    """)


    # Box about greedings

    # For gif
    gif = load_lottie('https://assets5.lottiefiles.com/packages/lf20_syglwy7h.json')

    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.header("What this app does")
            st.write("##")
            st.write(
                """
                - Looks for Job postings on [Indeed.com](https://uk.indeed.com/?from=gnav-homepage)
                - Filter postings based on the companies that are eligible to provide a visa based on [gov.uk](https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers)
                - Display only the postings of those companies
                - Allows you go to the specific posting on Indeed in order to make your application

                :point_down: If you want give it a try below ... it may take some minutes to run :point_down:
                """
            )
        with right_column:
            st_lottie(gif, height=300)


    # Creating the input section

    # Initializing the state of the button
    if 'button_search' not in st.session_state:
        st.session_state.button_search = False 



    ## Creating the input information

    st.text_input('Role that you want', key='role')

    type_options = ['Full-time','Permanent','Part-time','Internship','Apprenticeship','Temporary','Contract', 'Volunteer']

    type_job =  st.selectbox('Select your Job type', type_options)

    if type_job=='Full-time':
        st.session_state.jobtype = 'fulltime'
    elif type_job=='Permanent':
        st.session_state.jobtype = 'permanent'
    elif type_job=='Part-time':
        st.session_state.jobtype = 'parttime'
    elif type_job=='Internship':
        st.session_state.jobtype = 'internship'
    elif type_job=='Apprenticeship':
        st.session_state.jobtype = 'apprenticeship'
    elif type_job=='Temporary':
        st.session_state.jobtype = 'temporary'
    elif type_job=='Contract':
        st.session_state.jobtype = 'contract'
    elif type_job=='Volunteer':
        st.session_state.jobtype = 'volunteer'


    st.radio('City you want to work', ['London'] ,key='place')

    button_search = st.button('Search Jobs')


    # Creating a functionality of the app

    if button_search:
        st.session_state.button_search = True

        # Initializing the state of the type
        if 'jobtype' not in st.session_state:
            st.session_state.button_search = 'fulltime'

    if st.session_state.button_search:
        # Scrape the Job Listings
        data = scrape(st.session_state['role'],st.session_state['place'], st.session_state['jobtype'])
        # Do the screening of the postings
        results = job_screening(data)

        # Creating the filters to sort
        option_list = list(results.columns[ :-1])
        sort_columns = st.multiselect('Filter the results', option_list)
        #button_filter = st.button('Filter Jobs'

        results = results.sort_values(sort_columns) 

        # Creating a see_Job column with hyperlinks
        results['See_Job'] = results['Job_Link'].apply(make_clickable)
        # Print the table
        st.write(HTML(results.drop('Job_Link',axis=1).to_html(escape=False)), unsafe_allow_html=True)


        # Creating the download link
        st.markdown(filedownload(results), unsafe_allow_html=True) 

### Creating the second tab
elif selected == 'Visa Providers':
    
    st.write("""
    # Here you can see the full list of the companies that provide Visa
    """)
    
    with st.container():
        st.write("---")
        left_column, right_column = st.columns([1,1.5])
    with left_column: 
        st.write("""#### Top city:""")
        st.metric(label="London", value="20,998", delta="38%")
        st.write(""" """)
        
    with right_column: 
        #providers = pd.read_csv('Companies.csv')
        #st.dataframe(providers.drop(['County','City'],axis=1))
        st.write("""
    #### Next 5 cities:
    """)
        providers = pd.read_csv('Worker_and_Temporary_Worker.csv', sep=';')
    
        providers['Town/City'].replace({'LONDON':'London','Lonond':'London','london':'London','Lodnon':'London'}, inplace=True)
        graph = providers['Town/City'].value_counts()[1:6]
        st.bar_chart(graph)
    
    st.dataframe(providers[['Organisation Name','Town/City','Type & Rating','Route']])
    
    
    
elif selected == 'About Me':
    
    
    with st.container():
        left_column, right_column = st.columns(2)
        with left_column:
            st.header("Hey there! :wave:")
            st.write("##")
            st.write(
                """
                A litle information about me:
                - Info 1 
                - info 2
                """
            )
        with right_column:
            image = Image.open('7744517-kg.png')
            st.image(image,width = 300)