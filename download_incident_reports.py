# %%
import pandas as pd
import numpy as np
from rich import print
import urllib.request
from rich.progress import track
import os

# Read in the data from the website
data = pd.read_html("https://dcf.wisconsin.gov/cps/incidents")[0]
# Fill "Practice Review?" column with "No" if NaN
data.loc[ data[data.columns[2]] != data[data.columns[2]], data.columns[2] ] = "No"
# Convert date column to datetime
data[data.columns[1]] = pd.to_datetime(data[data.columns[1]])
# Remove last column
data = data[data.columns[:-1]]
# Fill 90 Day and 6 Month columbn with "No" if NaN
data.loc[ data[data.columns[4]] != data[data.columns[4]], data.columns[4] ] = "No"
data.loc[ data[data.columns[5]] != data[data.columns[5]], data.columns[5] ] = "No"
# %%
# Iterate through the rows of the dataframe and create a list of PDF URLs
pdf_urls = []
year_list = []
for index, row in data.iterrows():
    year = row[1].year
    file = row[3].lower()
    url = f"https://dcf.wisconsin.gov/files/cps/notifications/pdf/{year}/{file}.pdf"
    pdf_urls.append(url)
    year_list.append(year)
    

# %%

# Directory to save the PDF files in
directory = './data/WI/Notifications/'

# Create a list of problematic URLs
problem_urls = []

# Loop through the PDF URLs and download each file
for i in track(range(0, len(pdf_urls)), description="Downloading PDFs"):
    filename = url.split('/')[-1]
    if not os.path.exists(directory + f"/{year_list[i]}/"):
        os.makedirs(directory + f"/{year_list[i]}/")
    filepath = directory + f"/{year_list[i]}/" + filename
    try: 
        urllib.request.urlretrieve(url, filepath)
    except:
        problem_urls.append(url)
        # print(f"Error downloading {url}")
# %%
import re
import PyPDF2

# define a function to extract text from a PDF file
def extract_text(filepath):

    # Create a dictionary to store the data
    data = {}
    data["notification"] = filepath.split("/")[-1].split(".")[0]
    # Open the PDF file in read-binary mode
    with open(filepath, 'rb') as file:
        # Create a PDF reader object
        reader = PyPDF2.PdfReader(file)

        # Get the first page of the PDF file
        page = reader.pages[0]

        # Extract the text from the first page
        text = page.extract_text()

        # Split in lines
        lines = text.split('\n')

        des_1 = False
        des_2 = False
        des_3 = False
        des_4 = False
        in_home = False
        out_home = False
        # Find:
        #  Suspected Incident Description: (index)
        #  Age: (index)
        # Child's Residence: (index)
        for i, line in enumerate(lines):
            if 'suspected incident description' in line.lower():
                index_desc = i
            if 'age:' in line.lower():
                index_age = i
            if 'child\'s residence' in line.lower():
                index_res = i
        # Check if indexs were found

        if "ý" in lines[index_desc]:
            if "serious injury" in lines[index_desc].lower().split("ý")[1]:
                des_1 = True
            else:
                des_2 = True
        if "ý" in lines[index_desc+1]:
            if "egregious" in lines[index_desc+1].lower().split("ý")[1]:
                des_3 = True
            else:
                des_4 = True

        data["des_1"] = des_1
        data["des_2"] = des_2
        data["des_3"] = des_3
        data["des_4"] = des_4

        # Extract age
        age_pattern = r"Age:\s*(?:(\d+)\s*year(?:s)?(?:,\s*)?)?(?:(\d+)\s*week(?:s)?(?:,\s*)?)?(?:(\d+)\s*day(?:s)?(?:\s*)?)?"
        age_match = re.search(age_pattern, lines[index_age], re.IGNORECASE)
        if age_match.group(1):
            age = age_match.group(1)
            if age_match.group(2):
                age += "y" + age_match.group(2) + "w"
                if age_match.group(3):
                    age += age_match.group(3) + "d"
            elif age_match.group(3):
                age = age_match.group(3) + "d"
        else:
            if age_match.group(2):
                age = age_match.group(2) + "w"
                if age_match.group(3):
                    age += age_match.group(3) + "d"
            elif age_match.group(3):
                age = age_match.group(3) + "d"
            else:
                age = ""
        
        # Extract gender
        gender_pattern = r"Gender:\s+(\w)"
        gender_match = re.search(gender_pattern, lines[index_age])
        try:
            gender = gender_match.group(1)
        except:
            gender = "Missing"

        data["age"] = age
        data["gender"] = gender

        if "in home" in lines[index_res].lower().split("ý")[1]:
            in_home = True
        else:
            out_home = True

        data["in_home"] = in_home
        data["out_home"] = out_home

        return data

# %%
# Add columns to the dataframe
data["age"] = np.nan
data["gender"] = np.nan
data["in_home"] = np.nan
data["out_home"] = np.nan
data["Serious Injury"] = np.nan
data["Death / Alleged maltreatment"] = np.nan
data["Egregious incident"] = np.nan
data["Death / Alleged suicide in out-of-home care"] = np.nan
data["status"] = "No PDF"

years = range(2016, 2024)
for year in years:
# year = 2023
    pdf_list = os.listdir(f'data/WI/Notifications/{year}/')

    for pdf_file in track(pdf_list, description=f"Processing PDFs year {year}"):
        pdf_path = f'data/WI/Notifications/{year}/{pdf_file}'
        ind_ = data[data.Notification.str.lower() == pdf_file[:-4]].index
        try:
            data_pdf = extract_text(pdf_path)
        except:
            data.loc[ind_, "status"] = "Error Processing"
            continue
        # Find the notification in the dataframe
        data.loc[ind_, "age"]      = data_pdf["age"]
        data.loc[ind_, "gender"]   = data_pdf["gender"]
        data.loc[ind_, "in_home"]  = data_pdf["in_home"]
        data.loc[ind_, "out_home"] = data_pdf["out_home"]
        data.loc[ind_, "Serious Injury"]     = data_pdf["des_1"]
        data.loc[ind_, "Death / Alleged maltreatment"] = data_pdf["des_2"]
        data.loc[ind_, "Egregious incident"] = data_pdf["des_3"]
        data.loc[ind_, "Death / Alleged suicide in out-of-home care"] = data_pdf["des_4"]
        data.loc[ind_, "status"] = "Done"

# Save to csv







    # # Search for a pattern in the text to find the checkboxes
    # pattern = r'\[(X| )\] Checkbox 1\n\[(X| )\] Checkbox 2\n\[(X| )\] Checkbox 3'
    # match = re.search(pattern, text)

    # # Check if the checkboxes are checked
    # if match:
    #     checkbox1_checked = match.group(1) == 'X'
    #     checkbox2_checked = match.group(2) == 'X'
    #     checkbox3_checked = match.group(3) == 'X'
    #     print(f'Checkbox 1 is checked: {checkbox1_checked}')
    #     print(f'Checkbox 2 is checked: {checkbox2_checked}')
    #     print(f'Checkbox 3 is checked: {checkbox3_checked}')

# %%
data.to_csv("./data/WI/dataset.csv", index=False)
# %%