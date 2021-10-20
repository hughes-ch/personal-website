<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        {% include '_style.html' %}
        <title>RSS Feed - <xsl:value-of select="/rss/channel/title"/></title>
      </head>
      <body>
        <div class='page-content'>
          <div class='rss'>
            <a target='_blank' class='link'>
              <xsl:attribute name='href'>
                <xsl:value-of select='/rss/channel/link'/>
              </xsl:attribute>
              <h1><xsl:value-of select="/rss/channel/title"/></h1>
            </a>
            <p class='caption'>A blog by Chris Hughes</p>
            <xsl:for-each select="/rss/channel/item">
              <a target='_blank' class='link'>
                <xsl:attribute name='href'>
                  <xsl:value-of select='link'/>
                </xsl:attribute>
                <div>
                  <h2><xsl:value-of select="title"/></h2>
                  <time><xsl:value-of select='pubDate'/></time>
                  <p><xsl:value-of select='description'/></p>
                </div>
              </a>
              <hr/>
            </xsl:for-each>
          </div>
          {% include '_footer.html' %}
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
