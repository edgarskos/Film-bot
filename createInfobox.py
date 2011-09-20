#!/usr/bin/python
# -*- coding: utf-8  -*-
#

import wikipedia as pywikibot
import pagegenerators
from pywikibot import i18n
import imdb
import re
import Film
import sys

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class InfoboxBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator, img):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
        """
        self.generator = generator
        # Set the edit summary message
        self.summary = i18n.twtranslate(pywikibot.getSite(), 'basic-changing')
        
        self.log = codecs.open('logInfobox.txt', 'w', 'utf-8')
        self.img = img
        self.imdbNum = 0
        self.templateRegex = re.compile("{{.*}}") #This is how templates are in wikipedia
        self.referenceRegex = re.compile("(<ref.*?/(ref)?>)+")
        self.commentRegex = re.compile("<!--.*?-->")
        self.wikilinkRegex = re.compile("\[\[.*\|.*\]\]")
        
        infoTemp = pywikibot.Page(pywikibot.getSite(), "Template:Infobox_film/doc").get()
        infoTempStart = infoTemp.find("{{Infobox film") + 2
        bracketCount = 2
        infoTempEnd = infoTempStart
        while bracketCount != 0 :
          infoTempEnd += 1
          if infoTemp[infoTempEnd:infoTempEnd+1] == "{":
            bracketCount += 1
          elif infoTemp[infoTempEnd:infoTempEnd+1] == "}":
            bracketCount -= 1
        self.infoboxTemplate = re.sub(self.commentRegex, "", infoTemp[infoTempStart - 2:infoTempEnd+1])

    def run(self):
        for page in self.generator:
            self.treat(page)

    def treat(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        text = self.load(page)
        if not text:
            return
            
        ####self.imdbNum = 
        if re.subn("{{IMDb title.*?}}", "", text)[1] == 1: #If there is only 1 imdb link on the page search for the info
          if re.search("[0-9]{6,7}", re.search("{{IMDb title.*?}}", text).group()):
            self.imdbNum = re.search("[0-9]{6,7}", re.search("{{IMDb title.*?}}", text).group()).group()
        else:
          self.imdbNum = 0
        
        
        if(self.imdbNum != 0):
          movie = imdb.IMDb().get_movie(self.imdbNum)
          filmBot = Film.FilmBot(page, 1)
          newBox = filmBot.addImdbInfo(self.infoboxTemplate, movie)
          newBox = self.addNewInfo(newBox, page.title(), movie)
                
          #remove typically unused parameters
          if re.search("\| image size *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| image size *=.*?\n", "", newBox)
          if re.search("\| narrator *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| narrator *=.*?\n", "", newBox)
          if re.search("\| border *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| border *=.*?\n", "", newBox)
          if re.search("\| alt *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| alt *=.*?\n", "", newBox)
          if re.search("\| based on *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| based on *=.*?\n", "| based on       = <!-- {{based on|title of the original work|writer of the original work}} -->\n", newBox)
              
        pywikibot.output(newBox)
        self.log.write(newBox)
    
    def addNewInfo(self, infobox, pageTitle, movie):
      for field in re.sub("<ref.*?/(ref)?>", " reference ", re.sub("{{.*}}", "template", infobox)).split("|"):
        data = ""
        try: field.split("=")[1]
        except IndexError:
          sys.exc_clear() #skip it if there is an index error, means it has no "=", invalid field
        else:
          if(field.split("=")[1].strip() == ""): #fill in fields without data
            if(field.split("=")[0].strip() == "name"):
              data = pageTitle
              infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + data + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
            if(field.split("=")[0].strip() == "image") and self.img:
              if(movie.get('year')):
                year = str(movie.get('year'))
              else:
                year = ""
              data = re.sub(" ", "", pageTitle) + year + ".jpg"
              infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + data + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
              
      return infobox
              
    def load(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        try:
            # Load the page
            text = page.get()
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None
        
def main():
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitleParts = []
    img = False

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
      if arg.startswith("-img"):
        img = True
      else:
        # check if a standard argument like
        # -start:XYZ or -ref:Asdf was given.
        if not genFactory.handleArg(arg):
          pageTitleParts.append(arg)

    if pageTitleParts != []:
      # We will only work on a single page.
      pageTitle = ' '.join(pageTitleParts)
      page = pywikibot.Page(pywikibot.getSite(), pageTitle)
      gen = iter([page])

    if not gen:
      gen = genFactory.getCombinedGenerator()
    if gen:
      # The preloading generator is responsible for downloading multiple
      # pages from the wiki simultaneously.
      gen = pagegenerators.PreloadingGenerator(gen)
      bot = InfoboxBot(gen, img)
      bot.run()
    else:
      pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()