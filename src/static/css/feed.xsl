<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
      </head>
      <body>
        <div class='page-content'>
          <div class='title-block'>
            <h1>Test</h1>
          </div>
          <!--
          <xsl:for-each select="/rss/channel/item">
            <div class="item inner">
              <div class="item_meta">
                <span><xsl:value-of select="pubDate" /></span>
                <xsl:if test="itunes:duration">
                  &#x02022;
                  <span><xsl:value-of select="itunes:duration" /></span>
                </xsl:if>
              </div>
              <h2>
                <a target="_blank">
                  <xsl:attribute name="href">
                    <xsl:value-of select="link"/>
                  </xsl:attribute>
                  <xsl:value-of select="title"/>
                </a>
              </h2>
              <xsl:if test="itunes:subtitle">
                <h3><xsl:value-of select="itunes:subtitle" /></h3>
              </xsl:if>
              <xsl:if test="itunes:duration">
                <audio controls="true" preload="none">
                  <xsl:attribute name="src">
                    <xsl:value-of select="enclosure/@url"/>
                  </xsl:attribute>
                </audio>
              </xsl:if>
            </div>
          </xsl:for-each>
          <div class="typlog-foot">
            <a class="title" href="https://typlog.com/?utm_medium=feed">Typlog</a>
            <nav>
              <a href="https://typlog.com/about?utm_medium=feed">About</a>
              <a href="https://typlog.com/terms?utm_medium=feed">Terms</a>
            </nav>
          </div>
-->
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
