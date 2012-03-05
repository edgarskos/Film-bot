#!/usr/bin/python

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
import subprocess
import filmsettings

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class FilmBannerBot:

  def __init__(self, generator):
    self.generator = generator
    self.chrome = filmsettings.getChrome()
    self.count = 0
    
  def run(self):
    for page in self.generator:
      pywikibot.output(page.title())
      if(page.title().lower().find("user:") == -1 and page.title().lower().find("wikipedia talk:") == -1 and page.title().lower().find("category:") == -1):
        self.check(page.toggleTalkPage(), page)
  
  def check(self, talkPage, page):
    talkText = self.load(talkPage)
    pageText = self.load(page)
    if self.check2(talkText, pageText): #yes I need to change this name
      self.open(talkPage)        
  
  #Use for upkeep, brings in texts.
  def check2(self, talkText, pageText):
    if not talkText:
      if pageText: #only open talk pages that aren't on redirects. Freaking WP:CAT
        if pageText.lower().find("infobox television") == -1:
          return True
    elif not re.search("\{\{(wp|wikiproject)?.?film", talkText.lower()):
      if pageText.lower().find("infobox television") == -1 and talkText.lower().find("wikiproject anime and manga") == -1 and pageText.lower().find("infobox album") == -1 and talkText.lower().find("wikiProject songs") == -1 and talkText.lower().find("family-guy=yes") == -1:
        return True
    return False
  
  
  def open(self, talkPage):
    if self.count == 10:
      choice = pywikibot.inputChoice("This is a wait", ['Yes', 'No'], ['y', 'N'], 'N')
      self.count = 0
    self.count += 1
    Chrome = subprocess.Popen(self.chrome+' '+"https://secure.wikimedia.org/wikipedia/en/wiki/"+talkPage.title().replace(" ", "_").encode('utf-8', 'replace')+"?action=edit")
    
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
  genFactory = pagegenerators.GeneratorFactory()
  # The generator gives the pages that should be worked upon.
  gen = None
  pageTitleParts = []
  
  for arg in pywikibot.handleArgs():
    if arg.startswith("-reg"):
      arg = '-transcludes:Infobox film'
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
      bot = FilmBannerBot(gen)
      bot.run()
  else:
      pywikibot.showHelp()
    


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()