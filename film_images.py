#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
The following parameters are supported:

&params;

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""

import wikipedia as pywikibot
import pagegenerators
from pywikibot import i18n
import re
import editarticle
import sys
import codecs
import urllib
import subprocess
import Film
import msvcrt
import filmfunctions

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class FilmImageBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
        """
        self.generator = generator
        self.imdbNum = "0"
        self.chrome = "C:\Documents and Settings\\Desktop\GoogleChromePortable\GoogleChromePortable.exe"
        # Set the edit summary message
        self.summary = i18n.twtranslate(pywikibot.getSite(), 'basic-changing')
        self.hasImagestack = []
        self.newImageDict = dict()

    def run(self):
      for page in self.generator:
        text = self.load(page)
        self.treat(text, page.title())
        key = self.kbfunc()
        if(len(self.hasImagestack) > 50 or len(self.newImageDict) > 50): #don't let the stacks get too big
          key = "h"
        if (key == "o"):
          if(len(self.hasImagestack) != 0):
            self.doHasImage()
          elif(len(self.newImageDict) != 0):
            self.doNewImage()
          else:
            pywikibot.output("No Items on stack")
        elif(key == "h"): #this is HELP, just do all items in all stacks.
          while(len(self.newImageDict) != 0): #do all the ones that need an image
            self.doNewImage()
            choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
          while(len(self.hasImagestack) != 0): #then do all the ones that have an image
            self.doHasImage()
            choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
        elif(key == "p"): #just pause if the key is P
          choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
      #Finish off the rest of the stacks.
      while(len(self.newImageDict) != 0):
        self.doNewImage()
        choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
      while(len(self.hasImagestack) != 0):
        self.doHasImage()
        choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
    
    def kbfunc(self):
      return msvcrt.getch() if msvcrt.kbhit() else "Z"
      
    def doNewImage(self):
      ppp = self.newImageDict.popitem()
      filmBot = Film.FilmBot(iter([pywikibot.Page(pywikibot.getSite(), ppp[0])]), 1)
      filmBot.run()
      spNotepad = subprocess.Popen("notepad C:\pywikipedia\log.txt")
      spChrome = subprocess.Popen(self.chrome+' '+"http://www.movieposterdb.com/search/?query="+ppp[1])
      spChrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+ppp[0].encode('utf-8', 'replace'))
      
    def doHasImage(self):
      ppp = self.hasImagestack.pop()
      Chrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+ppp)
      Chrome3 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/w/index.php?title=Talk:"+ppp+"&action=edit")

    def treat(self, text, title):
        """
        Loads the given page, does some changes, and saves it.
        """
        if not text:
            return
        pywikibot.output(title)
        
        noSearch = 0;
        ###FIND IF TEXT HAS IMAGE
        infoboxStart = text.find("Infobox film")
        #get infobox that is there.
        if infoboxStart != -1: #infobox exists
          #find the end of the infobox but must account for other templates that are inside the infobox. Search for ending brackets by each character. For each
          #  new open bracket found add 1, then when finding ending brackets remove 1. This will find the ending position of the infobox while ignoring any
          #  and ALL templates that are found inside. Regex doesn't work here :(
          bracketCount = 2
          infoboxEnd = infoboxStart
          while bracketCount != 0 :
            infoboxEnd += 1
            if text[infoboxEnd:infoboxEnd+1] == "{":
              bracketCount += 1
            elif text[infoboxEnd:infoboxEnd+1] == "}":
              bracketCount -= 1
          infobox = text[infoboxStart:infoboxEnd-1]
          infoSplit = re.sub("<ref.*?/(ref)?>", " reference ", re.sub("{{.*}}", "template", infobox)).split("|")
          for field in infoSplit:
            try: field.split("=")[1]
            except IndexError:
              sys.exc_clear() #skip it if there is an index error, means it has no "=", invalid field
            else:
              if field.split("=")[0].strip() == "image" and not field.split("=")[1].strip() == "":
                pywikibot.output("Already has image")
                noSearch = 1
                self.hasImagestack.append(title.replace(" ", "_").encode('utf-8', 'replace'))
        elif(text.find(r"(i|I)nfobox") != -1): #infox doesn't exists
          pywikibot.output("Page doesn't have an infobox")
        
        if noSearch == 0 :
          ####self.imdbNum = 
          if re.subn("{{imdb title.*?}}", "", text.lower())[1] == 1: #If there is only 1 imdb link on the page search for the info
            if re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()):
              self.imdbNum = re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()).group()
          
              f = urllib.urlopen("http://www.movieposterdb.com/search/?query="+self.imdbNum)
              s = f.read()
              f.close()
              if(s.find("No results") == -1):
                pywikibot.output("YES!")
                self.newImageDict[title.replace(" ", "_")] = self.imdbNum
              else:
                pywikibot.output("No Image -> IMDB = "+self.imdbNum)
          else:
            pywikibot.output("No IMDB link  " + self.imdbNum)
          
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

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
      if arg.startswith("-reg"):
        arg = '-cat:Film articles needing an image'
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
        gen = pagegenerators.PreloadingGenerator(filmfunctions.PagesFromTalkPagesGenerator(gen))
        bot = FilmImageBot(gen)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
