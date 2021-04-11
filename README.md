# MyWorld

Short program that compares and displayed data about countrys with a simple and friendly GUI

To run the code you will need:

* [BeautifulSoup 4](https://pypi.org/project/bs4/)
* [JSON](https://pypi.org/project/jsonlib/)
* [CSV](https://pypi.org/project/python-csv/)
* [Plotly](https://pypi.org/project/plotly/)
* [Pandas](https://pypi.org/project/pandas2/)
* [Numpy](https://pypi.org/project/numpy/)
* [Matplotlib](https://pypi.org/project/matplotlib/)
* [os](https://pypi.org/project/os-win/)
* [cloudconverter](https://pypi.org/project/cloudconvert/) 
  * And it's API key
* [tkinter](https://pypi.org/project/tkinter-math/) 
* [plotly](https://pypi.org/project/plotly/)


Notes:

In function $Country.compare(self, other)$ there are 2 lines of code that are commented out:
```flag = get_img(self.flag, "img1.jpg")```
This is due to API "cloudConverter" only accepting up to 25 converts per day
With the lines commented out the flag pictures are incorrect!

Sometimes the graphs don't appear untill the GUI is closed!

