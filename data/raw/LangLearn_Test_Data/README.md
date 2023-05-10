==== LangLearn Test Data - EVALITA 2023 ====

This folder contains the test data for the Language Learning Development (LangLearn) shared task at EVALITA 2023.

The two folders contains the training data for the **CItA** and **COWS-L2H**. Each folder contains two files:
-- **Test_CItA.tsv/Test_COWS-L2H.tsv**: the file containing pairs of essays (each written by the same student) whose order has to be predicted. The file reports the following information:
	- Essay_1: id (randomly generated) of the one of the two essays of the pair;
	- Essay_2: id (randomly generated) of the the other of the two essays of the pair;
	- Order_1: Time of writing of the essay written as first;	
	- Order_2: Time of writing of the essay written as second;
	
**Important:** Note that, unlike in the Train file, here the essay ids are presented in random order; Order_1 and Order_2, on the other hand, provide information on the time interval between the two essays in the pair to be predicted. 
	
-- **Essays_Test_CItA.xml/Essays_Test_COWS-L2H.xml**: an .xml file that contains the essays with randomly generated document IDs.

==== Systems Predictions ====

Participants are required to add a new column (titled "Pred") to the test file. For each pair, participants will enter in the 'Pred' colum their predicted label.
Note that '0' indicates that Essay_1 was written before Essay_2, while '1' indicates that Essay_2 was written before Essay_1.

== Additional Info == 

*Test_CItA.tsv*: The codes in columns "Order_1" and "Order_2" have the following format: "Year + _ + Essay number". "Year" can be 1 or 2 depending on whether the essays were written in the first and second year of lower secondary school. "Essay number" shows the progressive number of the essay in that year. For example, 1_4 corresponds to the fourth essay written during the first year.

*Test_COWS-L2H.tsv*: The codes in columns "Order_1" and "Order_2" contain time information and should be read as follows: the academic terms (quarters) and year. For example, F20 is Fall 2020. The academic terms cover the following time spans: W goes from January to March, S from April to June, SU from July to September, and F from October to December.

*Essays_Test_CItA.xml/Essays_Test_COWS-L2H.xml*: For each essay in the essays file you will have a `<doc>` element (with the corresponding *id*) containing the text of the corresponding document.
In order to parse each `<doc>` element we suggest you to use the `xml.etree.ElementTree` python module as follows:

```
import xml.etree.ElementTree as ET

tree = ET.parse('Essays_CItA.xml')
root= tree.getroot()
for content in root.iter('doc'):
	print('Page id: ', content.get('id'))
	print('Page text: ', content.text)
```
