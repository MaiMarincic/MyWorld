#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests as rq
import json
import csv
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from skimage import io
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
import os
from pdf2image import convert_from_path
import cloudconvert
import tkinter as tk
import tkinter.font as font
from tkinter import ttk
from matplotlib.pyplot import figure
import plotly.io as pio
import pathlib
pio.renderers.default = 'browser'


# In[2]:


API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMGFkY2Q2MmVjZDQyZmM0MjU1YWE5NzE2YWE1ZWRjN2U0OGQxZWJiZWFiMjNhY2U0MjgxZTg4YmQ1ZGZiY2Q2MWQ2NzQ0Y2ZhNjdiMzMxZWIiLCJpYXQiOjE2MTgwNzg0MjEuNDAyNTY0LCJuYmYiOjE2MTgwNzg0MjEuNDAyNTY2LCJleHAiOjQ3NzM3NTIwMjEuMzYyOTQ3LCJzdWIiOiI1MDI2NTAwNCIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay5yZWFkIiwidGFzay53cml0ZSIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQucmVhZCIsInByZXNldC53cml0ZSJdfQ.TIr5n8mbtAcvhClRxqvhRgtlP9vlK0UOsfs4CGKQvhmjzkd1yA9W6zGsJCbQz8DY96z0HmceGgN2pL2UmEy2Wyc_VXRA8ok_02nM07IUsNxeMnr-1j-DviF3VdVx8uFbqKt6hCrOddmkAn3PSOrMMSPiLyDK7iOJ6Cy0cdttnPbKD7KzfRfz8ijJZNtLs_NHNLZvvpuZV6wWQjEL0olyUvVrQoDdYW55mmEX3ZikVkMV7J8HWjNUmkoe1dy0e9EvU-qqwfuFQ7xWQIr0HRpV3TazuW9YZTG6TXYJOi_qw-baz7FussBsCiwz047WMTxyxaFm9k0udopyEsWoijTnu7HZUf77Q6wc-sBy3SNiLG2nUopYfm-GoOeqtoEFNt-u1eg5-TcUqX4iUOBFenR7i1nmC2cK-wcfQoyDKqTlxCJUXWSReejSmA3u2JweYl_JwGUllxy55t80RJP2FpmuAVr4KPVcfXwmpTtVCifuNA3vHkQBBQK65ObpDwQxk0bsPdT-yMmMPuFD-vIAZvnrHvdgjRD4BOV_6iFWuwYUP7HPSw9ZZ5Msmmhb8mE_cfTSPNY0UjytYn1Z1LhhlZtdXEcH_6-eztgxhI2YUbQYH_zg83mKZGtfvBxoiuQRP9MqTrZEQsoTo3zJYZyEHms-GFAoZHntI0pwIOCkfSDqLHs"


# In[3]:


#path = pathlib.Path(__file__).parent.absolute()


# In[19]:


def get_img(img_url, exp_file):
    #convert image from .svg to .jpg using cloudconvert
    cloudconvert.configure(api_key = API_KEY, sandbox = False)
    job = cloudconvert.Job.create(payload={
            "tasks": {
                "flag1": {
                    "operation": "import/url",
                    "url": img_url
                },
                "flag1conv": {
                    "operation": "convert",
                    "input_format": "svg",
                    "output_format": "jpg",
                    "engine": "imagemagick",
                    "input": [
                        "flag1"
                    ],
                    "fit": "max",
                    "strip": False,
                    "pixel_density": 300,
                    "filename": exp_file
                },
                "flag1exp": {
                    "operation": "export/url",
                    "input": [
                        "flag1conv"
                    ],
                    "inline": False,
                    "archive_multiple_files": False
                }
            }
        })

        job = cloudconvert.Job.wait(id=job['id'])

        for task in job["tasks"]:
            if task.get("name") == "flag1exp" and task.get("status") == "finished":
                export_task = task

        file = export_task.get("result").get("files")[0]
        cloudconvert.download(filename=file['filename'], url=file['url'])
        pass


# In[20]:


def lifeExpectancyParse(data):
    #average the Female and Male data for Life Expactancy
    if data:
        m = float(data[0])
        f = float(data[1])
        return (m+f)/2
    return None
def avrgSizeParse(data):
    #average the Female and Male data for Average BMI
    if data:
        m = data[0]
        f = data[1]
        
        return (float(m[3])+float(f[3]))/2
    return None


# In[6]:


class Country:
    #main data structure
    def __init__(self, data):
        self.name = data["name"]
        self.capital = data["capital"]
        self.alpha3code = data["alpha3Code"]
        self.region = data["region"]
        self.subregion = data["subregion"]
        self.population = data["population"]
        self.latlng = data["latlng"] 
        self.area = data["area"]
        self.gini = data["gini"]
        self.borders = data["borders"]
        self.flag = data["flag"]
        self.populationlog10 = None
        if self.population:
            self.populationlog10 = np.log10(data["population"])
        self.id = -1
        self.avrgSize = []
        self.lifeExpectancy = []
        
    def __str__(self):
        string = ""
        string += "{:>20s} | '{:s}'\n".format('Name', self.name)
        string += "{:>20s} | '{:s}'\n".format('Capital', self.capital)
        string += "{:>20s} | '{:s}'\n".format('Code', self.alpha3code)
        string += "{:>20s} | '{:s}'\n".format('Region', self.region)
        string += "{:>20s} | '{:s}'\n".format('Subregion', self.subregion)
        string += "{:>20s} | '{:,d}'\n".format('Population', self.population)
        if self.gini:
            string += "{:>20s} | '{:.2f}'\n".format('Gini', self.gini)
        string += "{:>20s} | '{:s}'\n".format('Avrage Size', ' / '.join(map(str, self.avrgSize)))
        string += "{:>20s} | '{:s}'\n".format('Life Expectancy', ' / '.join(map(str, self.lifeExpectancy)))
        return string
    
    def compare(self, other):
        def haversine_distance(lat1, lon1, lat2, lon2):
            #using haversine distance to calculate distance in KM between 2 points on the globe using coordinates
            r = 6371
            phi1 = np.radians(lat1)
            phi2 = np.radians(lat2)
            delta_phi = np.radians(lat2 - lat1)
            delta_lambda = np.radians(lon2 - lon1)
            a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2)**2
            res = r * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))
            return np.round(res, 2)

        figure(figsize=(30, 15), dpi=80)
        plt.figure(1)

        plt.subplot(1,3,1)
        #flag = get_img(self.flag, "img1.jpg")
        plt.title(self.name, fontsize=30)
        img = mpimg.imread("img1.jpg")
        plt.xticks([])
        plt.yticks([])
        plt.imshow(img)
        plt.subplot(1,3,3)
        plt.title(other.name, fontsize=30)
        #flag = get_img(other.flag, "img2.jpg")
        img = mpimg.imread("img2.jpg")
        plt.xticks([])
        plt.yticks([])
        plt.imshow(img)
        print("The distance between the two capitals is: " + str(haversine_distance(*self.latlng, *other.latlng)))
        
#Due to missing data some in some country's displaying the graphs isn't always possible; Should work in next version
    
#         if self.population and self.lifeExpectancy and self.gini and other.population and other.lifeExpectancy and other.gini:
#             labels = ["population", "life expectancy", "gini"]
#             country1 = [
#             self.population*100/(self.population+other.population), 
#             lifeExpectancyParse(self.lifeExpectancy)*100/(lifeExpectancyParse(self.lifeExpectancy)+ lifeExpectancyParse(other.lifeExpectancy), 
#             avrgSizeParse(self.gini)*100/(avrgSizeParse(self.gini)+avrgSizeParse(other.gini)))]
#             country2 = [
#             other.population*100/(other.population+self.population), 
#             lifeExpectancyParse(other.lifeExpectancy)*100/(lifeExpectancyParse(other.lifeExpectancy) + lifeExpectancyParse(self.lifeExpectancy)),
#             avrgSizeParse(other.gini*100)/(avrgSizeParse(other.gini)+avrgSizeParse(self.gini))]

#             plt.subplot(2,3,2)
#             plt.title("Comparison")
#             fig, ax = plt.subplots()
#             rects1 = ax.bar(x - width/2, men_means, width, label=self.name)
#             rects2 = ax.bar(x + width/2, women_means, width, label=other.name)

#             # Add some text for labels, title and custom x-axis tick labels, etc.
#             ax.set_ylabel('Scores')
#             ax.set_title('Scores by group and gender')
#             ax.set_xticks(x)
#             ax.set_xticklabels(labels)
#             ax.legend()

#             ax.bar_label(rects1, padding=3)
#             ax.bar_label(rects2, padding=3)

#             fig.tight_layout()

#             plt.show()
        
    def check(self):
        figure(figsize=(30, 15), dpi=80)
        plt.figure(1)
        plt.subplot(1,1,1)
        #flag = get_img(self.flag, "img1.jpg")
        plt.title(self.name, fontsize=30)
        img = mpimg.imread("img1.jpg")
        plt.imshow(img)
        print(self)


# In[7]:


def countryAPI():
    #restcountries API; return list of Class Country
    api_data = rq.get("https://restcountries.eu/rest/v2/all")
    api_data = api_data.json()
    countryList = []
    for x in api_data:
        countryList.append(Country(x))
    return countryList


# In[8]:


def wrong_name(n):
    #due to inconsistency in naming on different sites/api we keep track of the irregularities
    d_names = json.load(open("wrong_names.json", "r"))
    if n in d_names.keys():
        return d_names[n]
    else:
        return n


# In[9]:


def countryNames(country_list):
    #return the list of country names
    tab = []
    for country in country_list:
        tab.append(country.name)
    return tab


# In[10]:


def scrapeLifeExpectancy():
    #returns life expectancy based on country
    url_LE = "https://www.worlddata.info/life-expectancy.php"
    response = rq.get(url_LE)
    soup = BeautifulSoup(response.text, 'html.parser')
    table_LE = soup.find('div', class_= 'tablescroller')
    data_LE = []
    for t in table_LE.find_all('tr'):
        tmpLE = []
        for x in t.find_all('td'):
            tmpLE.append(x.text)
        data_LE.append(tmpLE)
    #print(data_LE)
    return (data_LE[1:])


# In[11]:


def scrapeAverageSize():
    #returns 2 lists (male, female) their AVG Height, Weight, BMI based on country
    url_AS = "https://www.worlddata.info/average-bodyheight.php"
    response = rq.get(url_AS)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup.prettify())
    table_AS = soup.find('div', {"id": "averageheights"})
    table_AS = table_AS.find_all('tr')
    data_AS = []
    x = table_AS[1].find_all('td')
    for t in table_AS:
        tmpAS = []
        for x in t.find_all('td'):
            tmpAS.append(wrong_name(x.text))
        data_AS.append(tmpAS)
    data_AS = data_AS[1:]
    data_AS_Male = data_AS[:len(data_AS)//2]
    data_AS_Female = data_AS[len(data_AS)//2 + 1:]
    return (data_AS_Male, data_AS_Female)


# In[12]:


def add_scraped_data(countryList):
    #self.avrgSize = []
    #self.lifeExpectanc = []
    def le_f(le):
        for el in le:
            name = el[0]
            male = float(el[1].split(" ")[0])
            female = float(el[2].split(" ")[0])
            birth_rate = float(el[3].split(" ")[0])
            death_rate = float(el[4].split(" ")[0])
            for country in countryList:
                if country.name == name:
                    country.lifeExpectancy = [male, female, birth_rate, death_rate]
                    break
        pass
    
    def av_f(avM, avF):
        for el in avM:
            name = el[0]
            height = float(el[1].split(" ")[0])
            weight = float(el[2].split(" ")[0])
            bmi = float(el[3])
            for country in countryList:
                if country.name == name:
                    country.avrgSize = [["Male: ", height, weight, bmi]]
                    break
        for el in avF:
            name = el[0]
            height = float(el[1].split(" ")[0])
            weight = float(el[2].split(" ")[0])
            bmi = float(el[3])
            for country in countryList:
                if country.name == name:
                    country.avrgSize += [["Female: ", height, weight, bmi]]
                    break
        pass
    
    le = scrapeLifeExpectancy()
    avM, avF = scrapeAverageSize()
    le_f(le)
    av_f(avM, avF)


# In[13]:


def link_countryList_world_map(countryList, world_map):
    #MAP countryList to world_map
    #VOID
    dID = {}
    for i, feature in enumerate(world_map["features"]):
        feature["id"] = i
        dID[feature["properties"]["gu_a3"]] = i

    for country in countryList:
        if country.alpha3code in dID.keys():
            country.id = dID[country.alpha3code]


# In[14]:


def create_cvs(countryList):
    #VOID
    with open('data.csv', mode='w', newline = '', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['name', 'alpha3Code', 'capital', 'population', 'id', 'gini', 'lifeExpectancy', 'avrgSize'])
        for country in countryList:
            #if country.id != -1:
            writer.writerow([country.name, country.alpha3code, country.capital, country.populationlog10, country.id, country.gini, lifeExpectancyParse(country.lifeExpectancy), avrgSizeParse(country.avrgSize)])


# In[15]:


def draw_fig(par="population", title="log10(population)"):
    world_map = json.load(open("world_map.json", "r"))
    df = pd.read_csv("data.csv")
    fig = px.choropleth(df, locations='id', geojson = world_map, color=par, title=title)
    fig.show()


# In[16]:


class MainApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("MyWorld - By Mai Marincic & Anej Muzic")
        self.master.geometry("1090x170")
        
        self.master.var_check_country = tk.StringVar(master)
        self.master.var_check_country.set("Slovenia")
        self.master.var_compare_country1 = tk.StringVar(master)
        self.master.var_compare_country1.set("Slovenia")
        self.master.var_compare_country2 = tk.StringVar(master)
        self.master.var_compare_country2.set("Slovenia")
        
        self.create_widgets()

    def checkF(self):
        country_name = self.master.var_check_country.get()
        for c in countryList:
            if c.name == country_name:
                country = c
                c.check()
        pass
    def populationF(self):
        draw_fig("population", "populationlog10")
        pass
    def giniF(self):
        draw_fig("gini", "Gini")
        pass
    def lifeExpectancyF(self):
        draw_fig("lifeExpectancy", "Average Life Expectancy for both male and female")
        pass
    def avrgSizeF(self):
        draw_fig("avrgSize", "Average BMI")
        pass
    def compareF(self):
        compare1_name = self.master.var_compare_country1.get()
        compare2_name = self.master.var_compare_country2.get()
        for c in countryList:
            if c.name == compare1_name:
                a = c
            if c.name == compare2_name:
                b = c
        a.compare(b)
        pass
    
    
    def create_widgets(self):
        
        my_font = font.Font(family='Helvetica')
        
        # ROW 0
        self.lb_world = tk.Label(self.master, text = "  World: ", font = ('Helvetica', 19, 'bold'))
        self.lb_world.grid(row=0, column=0)
        self.bt_population = tk.Button(self.master, text = " Population ", width = 20, font = my_font, bg="green", fg="white", command=self.populationF)
        self.bt_population.grid(row=0, column=1, padx=10, pady=10)
        self.bt_gini = tk.Button(self.master, text = " Gini ", width = 20, font = my_font, bg="green", fg="white", command=self.giniF)
        self.bt_gini.grid(row=0, column=2, padx=10, pady=10)
        self.bt_lifeExpectancy = tk.Button(self.master, text = " Life Expectancy ", width = 20, font = my_font, bg="green", fg="white", command=self.lifeExpectancyF)
        self.bt_lifeExpectancy.grid(row=0, column=3, padx=10, pady=10)
        self.bt_avrgSize = tk.Button(self.master, text =  " Average Size ", width = 20, font = my_font, bg="green", fg="white", command=self.avrgSizeF)
        self.bt_avrgSize.grid(row=0, column=4, padx=10, pady=10)
        
        #ROW 1
        self.lb_country = tk.Label(self.master, text = "  See country: ", font = ('Helvetica', 19, 'bold'))
        self.lb_country.grid(row=1, column=0)
        self.cm_country = ttk.Combobox(self.master, width = 30, textvariable = self.master.var_check_country)
        self.cm_country['values'] = countryNames(countryList)
        self.cm_country.grid(row=1, column=1)
        self.bt_check = tk.Button(self.master, text =  " Check ", width = 20, font = my_font, bg="green", fg="white", command=self.checkF)
        self.bt_check.grid(row=1, column=4, padx=10, pady=10)
        
        #ROW 2
        self.lb_compare1 = tk.Label(self.master, text = "  Compare country ", font = ('Helvetica', 19, 'bold'))
        self.lb_compare1.grid(row=2, column=0)
        self.cm_compare_country1 = ttk.Combobox(self.master, width = 30, textvariable = self.master.var_compare_country1)
        self.cm_compare_country1['values'] = countryNames(countryList)
        self.cm_compare_country1.grid(row=2, column=1)
        self.cm_compare_country2 = ttk.Combobox(self.master, width = 30, textvariable = self.master.var_compare_country2)
        self.cm_compare_country2['values'] = countryNames(countryList)
        self.lb_compare2 = tk.Label(self.master, text = "  and ", font = ('Helvetica', 19, 'bold'))
        self.lb_compare2.grid(row=2, column=2)
        self.cm_compare_country2.grid(row=2, column=3)
        self.bt_compare = tk.Button(self.master, text =  " Compare ", width = 20, font = my_font, bg="green", fg="white", command =self.compareF)
        self.bt_compare.grid(row=2, column=4, padx=10, pady=10)
    


# In[17]:


countryList = countryAPI()
def main():
    #INIT ALL THE BS
    add_scraped_data(countryList)
    world_map = json.load(open("world_map.json", "r"))
    link_countryList_world_map(countryList, world_map)
    create_cvs(countryList)
    
    #GUI BS
    root = tk.Tk()
    clicked = tk.IntVar()   
    clicked.set(1)
    app = MainApp(master=root)
    app.mainloop()
    
if __name__ == "__main__":
    main()

