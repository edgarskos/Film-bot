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

class FilmAssessBot:
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

    def run(self):
      for page in self.generator:
        text = self.load(page)
        self.treat(text, page)

    def treat(self, text, page):
        title = page.title()
        if not text:
            return
        pywikibot.output(title)
        
        task = ""
        image = ""
        infobox = ""
        banner = ""
        
        if text.lower().find("usa") != -1 or text.lower().find("america") != -1 or text.lower().find("film us") != -1:
          task = "|American-task-force=yes"
        elif text.lower().find("argentine") != -1:
          task = "|Argentine-task-force=yes"
        elif text.lower().find("australia") != -1:
          task = "|Australian-task-force=yes"
        elif text.lower().find("estonia") != -1 or text.lower().find("latvia") != -1 or text.lower().find("lithuania") != -1:
          task = "|Baltic-task-force=yes"
        elif text.lower().find("british") != -1 or text.lower().find("united kingdom") != -1 or text.lower().find("film uk") != -1:
          task = "|British-task-force=yes"
        elif text.lower().find("canada") != -1:
          task = "|Canadian-task-force=yes"
        elif text.lower().find("chinese") != -1:
          task = "|Chinese-task-force=yes"
        elif text.lower().find("france") != -1 or text.lower().find("french") != -1:
          task = "|French-task-force=yes"
        elif text.lower().find("german") != -1:
          task = "|German-task-force=yes"
        elif text.lower().find("indian") != -1:
          task = "|Indian-task-force=yes"
        elif text.lower().find("italian") != -1:
          task = "|Italian-task-force=yes"
        elif text.lower().find("japanese") != -1:
          task = "|Japanese-task-force=yes"
        elif text.lower().find("korean") != -1 or text.lower().find("korea") != -1:
          task = "|Korean-task-force=yes"
        elif text.lower().find("new zealand") != -1:
          task = "|NZ-task-force=yes"
        elif (text.lower().find("denmark") != -1 or text.lower().find("finland") != -1 or 
              text.lower().find("greenland") != -1 or text.lower().find("iceland") != -1 or 
              text.lower().find("norway") != -1 or text.lower().find("sweden") != -1 or 
              text.lower().find("swedish") != -1 or text.lower().find("danish") != -1):
          task = "|Nordic-task-force=yes"
        elif text.lower().find("persian") != -1:
          task = "|Persian-task-force=yes"
        elif (text.lower().find("burma") != -1 or text.lower().find("cambodia") != -1 or 
              text.lower().find("indonesia") != -1 or text.lower().find("malaysia") != -1 or 
              text.lower().find("philippines") != -1 or text.lower().find("singapore") != -1 or 
              text.lower().find("thailand") != -1 or text.lower().find("vietnam") != -1 or 
              text.lower().find("brunei") != -1 or text.lower().find("east timor") != -1 or 
              text.lower().find("laos") != -1):
          task = "|Southeast-task-force=yes"
        elif (text.lower().find("armenia") != -1 or text.lower().find("azerbaijan") != -1 or
              text.lower().find("belarus") != -1 or text.lower().find("georgia") != -1 or
              text.lower().find("kazakhstan") != -1 or text.lower().find("kyrgyzstan") != -1 or
              text.lower().find("russia") != -1 or text.lower().find("soviet union") != -1 or
              text.lower().find("tajikistan") != -1 or text.lower().find("ukraine") != -1 or
              text.lower().find("uzbekistan") != -1):
          task = "|Soviet-task-force=yes"
        elif text.lower().find("spain") != -1:
          task = "|Spanish-task-force=yes"
          
        
        spChrome = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+page.title().replace(" ", "_").encode('utf-8', 'replace'))
        
        tempClass = pywikibot.input("Input class")
        if tempClass != "":
          clas = "|class=" + tempClass
                 
          choice = pywikibot.inputChoice(u'Task force -> '+task+'?', ['Yes', 'No'], ['y', 'N'], 'N')
          if choice == 'n':
            temp = pywikibot.input("Input task force")
            if temp != "":
              task = "|" + temp + "-task-force=yes"
            else:
              task = ""
          
          #see if it has an infobox
          if not (re.search("infobox film", text, re.I) or re.search("infobox_film", text, re.I)):
            infobox = "|needs-infobox=yes"
          
          #see if it has an image
          if not (re.search(".jpg", text, re.I) or re.search(".gif", text, re.I)):
            image = "|needs-image=yes"
          
          banner = "{{Film" + clas + task + image + infobox + "}}" #these powers combined, into a banner
          
          #pywikibot.output(banner)
          
          talkText = self.load(page.toggleTalkPage())
          talkText = talkText.replace("|needs-image=yes", "")
          if(re.search("\{\{(wikiproject film|film|wpfilm).*\}\}", talkText, re.I)): 
            talkText = re.sub(r"\{\{(wikiproject film|film|wpfilm).*\}\}", banner, talkText, flags=re.IGNORECASE)#talkText.replace("\{\{(wikiproject film|film).*\}\}", banner, re.I)
          self.save(talkText, page.toggleTalkPage(), "update film banner")
          #choice = pywikibot.inputChoice(u'Task force -> '+task+'?', ['Yes', 'No'], ['y', 'N'], 'N')
         
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
          #else:
          #  Chrome3 = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/w/index.php?title=Talk:"+title+"&action=edit")
                  
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

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
      if arg.startswith("-reg"):
        arg = '-cat:Unassessed film articles'
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
        bot = FilmAssessBot(gen)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
