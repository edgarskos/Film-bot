import re

def countryToTemplate(countries):
  returned = ""
  dataSplit = re.sub(", ", "<br />", countries).split("<br />")
  for data in dataSplit:
  
    if(data.strip().lower() == "united states" or data.strip().lower() == "us" or data.strip().lower() == "usa" or data.strip().lower() == "{{usa}}" or data.strip().lower() == "{{us}}"): #if country is us change to {{filmUS}}
      data = "{{Film US}}"
    elif(data.strip().lower() == "uk" or data.strip().lower() == "united kingdom"):
      data = "{{Film UK}}"
    elif data.strip().lower() == "canada" or data.strip().lower() == "can" :
      data = "{{Film Canada}}"
    elif(data.strip().lower() == "india" or data.strip().lower() == "{{ind}}"):
      data = "{{Film India}}"
    elif data.strip().lower() == "afghanistan" :
      data = "{{Film Afghanistan}}"
    elif data.strip().lower() == "albania" :
      data = "{{Film Albania}}"
    elif data.strip().lower() == "algeria" :
      data = "{{Film Algeria}}"
    elif data.strip().lower() == "argentina" :
      data = "{{Film Argentina}}"
    elif data.strip().lower() == "armenia" :
      data = "{{Film Armenia}}"
    elif data.strip().lower() == "australia" :
      data = "{{Film Australia}}"
    elif data.strip().lower() == "austria" :
      data = "{{Film Austria}}"
    elif data.strip().lower() == "bangladesh" :
      data = "{{Film Bangladesh}}"
    elif data.strip().lower() == "belgium" :
      data = "{{Film Belgium}}"
    elif data.strip().lower() == "brazil" :
      data = "{{Film Brazil}}"
    elif data.strip().lower() == "bulgaria" :
      data = "{{Film Bulgaria}}"
    elif data.strip().lower() == "burkina faso" :
      data = "{{Film Burkina Faso}}"
    elif data.strip().lower() == "cambodia" :
      data = "{{Film Cambodia}}"
    elif data.strip().lower() == "chad" :
      data = "{{Film Chad}}"
    elif data.strip().lower() == "chile" :
      data = "{{Film Chile}}"
    elif(data.strip().lower() == "china"):
      data = "{{Film China}}"
    elif data.strip().lower() == "colombia" :
      data = "{{Film Colombia}}"
    elif data.strip().lower() == "croatia" :
      data = "{{Film Croatia}}"
    elif data.strip().lower() == "cuba" :
      data = "{{Film Cuba}}"
    elif data.strip().lower() == "czech republic" :
      data = "{{Film Czech Republic}}"
    elif data.strip().lower() == "czechoslovakia" :
      data = "{{Film Czechoslovakia}}"
    elif data.strip().lower() == "denmark" :
      data = "{{Film Denmark}}"
    elif data.strip().lower() == "ecuador" :
      data = "{{Film Ecuador}}"
    elif data.strip().lower() == "egypt" :
      data = "{{Film Egypt}}"
    elif data.strip().lower() == "finland" :
      data = "{{Film Finland}}"
    elif(data.strip().lower() == "france"):
      data = "{{Film France}}"
    elif(data.strip().lower() == "germany"):
      data = "{{Film Germany}}"
    elif data.strip().lower() == "greece" :
      data = "{{Film Greece}}"
    elif data.strip().lower() == "guinea" :
      data = "{{Film Guinea}}"
    elif data.strip().lower() == "haiti" :
      data = "{{Film Haiti}}"
    elif data.strip().lower() == "hong kong" :
      data = "{{Film Hong Kong}}"
    elif data.strip().lower() == "hungary" :
      data = "{{Film Hungary}}"
    elif data.strip().lower() == "iceland" :
      data = "{{Film Iceland}}"
    elif data.strip().lower() == "indonesia" :
      data = "{{Film Indonesia}}"
    elif data.strip().lower() == "iran" :
      data = "{{Film Iran}}"
    elif data.strip().lower() == "ireland" :
      data = "{{Film Ireland}}"
    elif data.strip().lower() == "israel" :
      data = "{{Film Israel}}"
    elif data.strip().lower() == "italy" :
      data = "{{Film Italy}}"
    elif data.strip().lower() == "japan" :
      data = "{{Film Japan}}"
    elif data.strip().lower() == "kazakhstan" :
      data = "{{Film Kazakhstan}}"
    elif data.strip().lower() == "kyrgyzstan" :
      data = "{{Film Kyrgyzstan}}"
    elif data.strip().lower() == "latvia" :
      data = "{{Film Latvia}}"
    elif data.strip().lower() == "lebanon" :
      data = "{{Film Lebanon}}"
    elif data.strip().lower() == "lithuania" :
      data = "{{Film Lithuania}}"
    elif data.strip().lower() == "luxembourg" :
      data = "{{Film Luxembourg}}"
    elif data.strip().lower() == "malaysia" :
      data = "{{Film Malaysia}}"
    elif data.strip().lower() == "mali" :
      data = "{{Film Mali}}"
    elif data.strip().lower() == "mexico" :
      data = "{{Film Mexico}}"
    elif data.strip().lower() == "morocco" :
      data = "{{Film Morocco}}"
    elif(data.strip().lower() == "the netherlands" or data.strip().lower() == "netherlands"):
      data = "{{Film Netherlands}}"
    elif data.strip().lower() == "new zealand" :
      data = "{{Film New Zealand}}"
    elif data.strip().lower() == "nigeria" :
      data = "{{Film Nigeria}}"
    elif data.strip().lower() == "norway" :
      data = "{{Film Norway}}"
    elif data.strip().lower() == "pakistan" :
      data = "{{Film Pakistan}}"
    elif data.strip().lower() == "palestine" :
      data = "{{Film Palestine}}"
    elif data.strip().lower() == "peru" :
      data = "{{Film Peru}}"
    elif data.strip().lower() == "philippines" :
      data = "{{Film Philippines}}"
    elif data.strip().lower() == "poland" :
      data = "{{Film Poland}}"
    elif data.strip().lower() == "portugal" :
      data = "{{Film Portugal}}"
    elif data.strip().lower() == "puerto rico" :
      data = "{{Film Puerto Rico}}"
    elif data.strip().lower() == "romania" :
      data = "{{Film Romania}}"
    elif data.strip().lower() == "russia" :
      data = "{{Film Russia}}"
    elif data.strip().lower() == "senegal" :
      data = "{{Film Senegal}}"
    elif data.strip().lower() == "serbia" :
      data = "{{Film Serbia}}"
    elif data.strip().lower() == "singapore" :
      data = "{{Film Singapore}}"
    elif data.strip().lower() == "south africa" :
      data = "{{Film South Africa}}"
    elif data.strip().lower() == "south korea" :
      data = "{{Film South Korea}}"
    elif data.strip().lower() == "ussr" :
      data = "{{Film USSR}}"
    elif data.strip().lower() == "spain" :
      data = "{{Film Spain}}"
    elif data.strip().lower() == "sri lanka" :
      data = "{{Film Sri Lanka}}"
    elif data.strip().lower() == "sweden" :
      data = "{{Film Sweden}}"
    elif data.strip().lower() == "switzerland" :
      data = "{{Film Switzerland}}"
    elif data.strip().lower() == "syria" :
      data = "{{Film Syria}}"
    elif data.strip().lower() == "taiwan" :
      data = "{{Film Taiwan}}"
    elif data.strip().lower() == "tajikistan" :
      data = "{{Film Tajikistan}}"
    elif data.strip().lower() == "thailand" :
      data = "{{Film Thailand}}"
    elif data.strip().lower() == "tunisia" :
      data = "{{Film Tunisia}}"
    elif data.strip().lower() == "turkey" :
      data = "{{Film Turkey}}"
    elif data.strip().lower() == "uae" :
      data = "{{Film UAE}}"
    elif data.strip().lower() == "ukraine" :
      data = "{{Film Ukraine}}"
    elif data.strip().lower() == "uruguay" :
      data = "{{Film Uruguay}}"
    elif data.strip().lower() == "venezuela" :
      data = "{{Film Venezuela}}"
    elif data.strip().lower() == "vietnam" :
      data = "{{Film Vietnam}}"
    elif data.strip().lower() == "yugoslavia" :
      data = "{{Film Yugoslavia}}"
      
    returned += data + "+"
    
  return re.sub("\+", "<br />", returned.rstrip("+"))