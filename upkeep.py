#!/usr/bin/python
"""
No parameters are supported.

Run as upkeep on categories already fully run with the bots
"""

import wikipedia as pywikibot
import pagegenerators
import Film
import film_banners as Banner
import film_images as Images
import film_assess as Assess
import createInfobox as Infobox
import re

def main():
  genFactory = pagegenerators.GeneratorFactory()
  args = []
  # The generator gives the pages that should be worked upon.
  for x in range(2010, 2019):
    args.append('-cat:'+str(x)+" films")
  
  args.append('-cat:Upcoming films')
  
  for t in args:
    gen = None
    pageTitleParts = []
  
    for arg in pywikibot.handleArgs(t):
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
        gen = pagegenerators.PreloadingGenerator(pagegenerators.PageWithTalkPageGenerator(gen))
        filmBot = Film.FilmBot(gen, False, False)
        bannerBot = Banner.FilmBannerBot(gen)
        imageBot = Images.FilmImageBot(gen, False, False)
        assessBot = Assess.FilmAssessBot(gen)
        infoboxBot = Infobox.InfoboxBot(gen, False, False, False)
        code = "ok"
        for page in gen:
          if(page.title().lower().find("user:") == -1 and page.title().lower().find("wikipedia talk:") == -1 and page.title().lower().find("category:") == -1):
            if not page.isTalkPage():
              pageText = filmBot.load(page)
              title = page.title()
              filmBot.treat(page, pageText)
              code = imageBot.treat(pageText, page)
            else:
              talkText = filmBot.load(page)
              if bannerBot.check2(talkText, pageText):
                bannerBot.open(page)
                pywikibot.output(code)
              elif(pageText): #if bannerbot is not needed
                if code == "has" and re.search("needs-image=yes", talkText):
                  imageBot.doHasImage(title, page)
                #elif (not (re.search("\.jpg", pageText, re.I) or re.search("\.gif", pageText, re.I) or re.search("\.png", pageText, re.I) or re.search("\.jpeg", pageText, re.I) or re.search("\.tif", pageText, re.I))) and not re.search("needs-image=yes", talkText, re.I) and not re.search("class=list", talkText, re.I):
                #  assessBot.treat(pageText, page.toggleTalkPage())
                elif code == "found" and re.search("needs-image=yes", talkText):
                  imageBot.doNewImage(title, page)
                elif code == "noinfobox":
                  infoboxBot.treat(page)
     
if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()