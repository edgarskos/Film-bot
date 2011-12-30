#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
The following parameters are supported:

&params;

-img              If given, doesn't do any real changes, but only shows
                  what would have been changed.
-info             Get the infobox data anyway, even if the page has an infobox                 
-imdb             If the page doesn't have an IMDB link, let the user input the number
                  instead of skipping the page.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""

import wikipedia as pywikibot
import pagegenerators
from pywikibot import i18n
import imdb
import re
import Film
import sys
import codecs
import subprocess
import filmfunctions
import filmsettings

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class InfoboxBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator, img, info, imdb):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
        """
        self.generator = generator
        # Set the edit summary message
        self.summary = i18n.twtranslate(pywikibot.getSite(), 'basic-changing')
        
        self.chrome = filmsettings.getChrome()
        self.img = img
        self.info = info
        self.imdb = imdb
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
        self.treat(pywikibot.Page(pywikibot.getSite(), page.title().replace("Talk:", "")))

    def treat(self, page):
      """
      Loads the given page, does some changes, and saves it.
      """
      text = self.load(page)
      if not text:
          return
      
      newBox = ""
      self.imdbNum = 0
      infoboxStart = text.find("Infobox film")
      #get infobox that is there.
      if infoboxStart == -1 or self.info: #infobox exists
        ####self.imdbNum = 
        if re.subn("{{imdb title.*?}}", "", text.lower())[1] == 1: #If there is only 1 imdb link on the page search for the info
          if re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()):
            self.imdbNum = re.search("[0-9]{6,7}", re.search("{{imdb title.*?}}", text.lower()).group()).group()
        elif self.imdb:
            self.imdbNum = int(pywikibot.input(page.title() + ": input IMDB num"))
        else:
          self.imdbNum = 0
        
        
        if(self.imdbNum != 0):
          movie = imdb.IMDb().get_movie(self.imdbNum)
          filmBot = Film.FilmBot(page, True, False)
          newBox = filmBot.addImdbInfo(self.infoboxTemplate, movie)
          newBox = self.addNewInfo(newBox, page.title(), movie)
                
          #remove typically unused parameters
          if re.search("\| image size *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| image size *=.*?\n", "", newBox)
          if re.search("\| narrator *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| narrator *=.*?\n", "", newBox)
          if re.search("\| border *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| border *=.*?\n", "", newBox)
          if re.search("\| based on *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| based on *=.*?\n", "", newBox)
          if not re.search("\| writer *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            if re.search("\| story *=.*?\n", newBox).group().split("=")[1].strip() == "" :
              newBox = re.sub("\| story *=.*?\n", "", newBox)
            if re.search("\| screenplay *=.*?\n", newBox).group().split("=")[1].strip() == "" :
               newBox = re.sub("\| screenplay *=.*?\n", "", newBox)
          elif not re.search("\| story *=.*?\n", newBox).group().split("=")[1].strip() == "" : #remove these fields if it has a writer and they're empty
            if re.search("\| writer *=.*?\n", newBox).group().split("=")[1].strip() == "" :
              newBox = re.sub("\| writer *=.*?\n", "", newBox)
            if re.search("\| screenplay *=.*?\n", newBox).group().split("=")[1].strip() == "" :
              newBox = re.sub("\| screenplay *=.*?\n", "", newBox)
            
          #add how to to fields
          #if re.search("\| based on *=.*?\n", newBox).group().split("=")[1].strip() == "" :
          #  newBox = re.sub("\| based on *=.*?\n", "| based on       = <!-- {{based on|title of the original work|writer of the original work}} -->\n", newBox)
          if re.search("\| released *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| released *=.*?\n", "| released       = <!-- {{Film date|Year|Month|Day|Location}} -->\n", newBox)
          if re.search("\| alt *=.*?\n", newBox).group().split("=")[1].strip() == "" :
            newBox = re.sub("\| alt *=.*?\n", "| alt            = <!-- see WP:ALT -->\n", newBox)              
              
          #pywikibot.output(newBox)
          log = codecs.open('logInfobox.txt', 'w', 'utf-8')
          log.write(newBox)
          log.close()
          start = 0
          while text[start:start+1] == "{":
            start += 2
            bracketCount = 2
            while bracketCount != 0 :
              start += 1
              if text[start:start+1] == "{":
                bracketCount += 1
              elif text[start:start+1] == "}":
                  bracketCount -= 1
            start += 1
            while re.search("\s", text[start:start+1]):
              start += 1
          text = filmBot.standardFixes(text)
          text = text[:start] +newBox + "\n" + text[start:]
          if self.save(text, page, "add infobox"):
            text = self.load(page.toggleTalkPage())
            text = text.replace("|needs-infobox=yes", "")
            self.save(text, page.toggleTalkPage(), "update film banner (has infobox)")
          else:
            spNotepad = subprocess.Popen("notepad C:\pywikipedia\logInfobox.txt")
            spChrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+page.title().replace(" ", "_").encode('utf-8', 'replace')+"?action=edit")
            choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
      else:
        pywikibot.output("HAS Infobox")
        spChrome2 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+page.title().replace(" ", "_").encode('utf-8', 'replace'))
        text = self.load(page.toggleTalkPage())
        text = text.replace("|needs-infobox=yes", "")
        self.save(text, page.toggleTalkPage(), "update film banner (has infobox)")
            
    def addNewInfo(self, infobox, pageTitle, movie):
      for field in re.sub("<ref.*?/(ref)?>", " reference ", re.sub("{{.*}}", "template", infobox)).split("|"):
        data = ""
        try: field.split("=")[1]
        except IndexError:
          sys.exc_clear() #skip it if there is an index error, means it has no "=", invalid field
        else:
          if field.split("=")[1].strip() == "": #fill in fields without data
            if field.split("=")[0].strip() == "name":
              if movie.has_key('title'):
                data = movie['title']
              else:
                data = pageTitle
              infobox = infobox[:infobox.find("=", infobox.find(field.split("=")[0]))+2] + data + infobox[infobox.find("=", infobox.find(field.split("=")[0]))+2:] 
            if (field.split("=")[0].strip() == "image") and self.img:
              if movie.has_key('year'):
                year = str(movie.get('year'))
              else:
                year = ""
              data = re.sub(" ", "", movie['title']) + year + ".jpg"
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
        
    def save(self, text, page, comment, minorEdit=False, botflag=False):
      # only save if something was changed
      if text != page.get():
        # Show the title of the page we're working on.
        # Highlight the title in purple.
        pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                         % page.title())
        # show what was changed
        pywikibot.showDiff(page.get(), text)
        
        pywikibot.output(u'Comment: %s' %comment)
        choice = pywikibot.inputChoice(
          u'Do you want to accept these changes?',
          ['Yes', 'No'], ['y', 'N'], 'N')
        if choice == 'y':
          try:
              # Save the page
              page.put(text, comment=comment,
                       minorEdit=minorEdit, botflag=botflag)
          except pywikibot.LockedPage:
              pywikibot.output(u"Page %s is locked; skipping."
                               % page.title(asLink=True))
          except pywikibot.EditConflict:
              pywikibot.output(
                  u'Skipping %s because of edit conflict'
                  % (page.title()))
          except pywikibot.SpamfilterError, error:
              pywikibot.output(
                  u'Cannot change %s because of spam blacklist entry %s'
                  % (page.title(), error.url))
          else:
              return True
      return False
        
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
    info = False
    imdb = False

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
      if arg.startswith("-img"):
        img = True
      elif arg.startswith("-info"):
        info = True
      elif arg.startswith("-imdb"):
        imdb = True
      elif arg.startswith("-reg"):
        arg = '-cat:Film articles needing an infobox'
        if not genFactory.handleArg(arg):
          pageTitleParts.append(arg)
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
      gen = pagegenerators.PreloadingGenerator(filmfunctions.PagesFromTalkPagesGenerator(gen))
      bot = InfoboxBot(gen, img, info, imdb)
      bot.run()
    else:
      pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
