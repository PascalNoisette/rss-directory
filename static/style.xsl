<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xsl:output method="html" indent="yes" omit-xml-declaration="yes" />

    <xsl:template match="/rss">
    <html>
    <head>
      <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
      <link rel="stylesheet" type="text/css" href="rss.css"/>
    </head>
    <body>
      <div id="feedHeaderContainer">
        <div id="feedHeader" dir="ltr" class="feedBackground">
            <div id="feedSubscribeLine">
              <label id="subscribeUsingDescription">Subscribe to this feed </label>
            </div>
        </div>
        <div id="feedHeaderContainerSpacer"></div>
    </div>
      <div class="rsshtml">
      <xsl:apply-templates select="channel" />
    </div>
    </body>
    </html>
    </xsl:template>


  <xsl:template match="channel">
    <div class="rsshtml-channel">
      <div class="rsshtml-title">
        <h1>
          <xsl:value-of select="title" />
        </h1>
        <h2>
          <xsl:value-of select="description" />
        </h2>
      </div>
      <xsl:apply-templates select="item" />
    </div>
  </xsl:template>

  <xsl:template match="item">
    <div class="rsshtml-item">
      <h3 class="rsshtml-item-title">
        <a href="{link}">
          <xsl:value-of select="title" />
        </a>
        <div class="rsshtml-item-subtitle">
          <xsl:value-of select="pubDate" />
        </div>
      </h3>
      <div class="rsshtml-item-description">
        <xsl:value-of select="description" />
      </div>
      <xsl:apply-templates select="enclosure" />

    </div>
    <div style="clear: both;"></div>
  </xsl:template>

  <xsl:template match="enclosure">
    <div xmlns="http://www.w3.org/1999/xhtml" class="enclosures">Media files
          <div class="enclosure">
            <img alt="" src="fileIcon.png" class="type-icon" />
            <a href="{@url}"><xsl:value-of select="@url" /></a>
          </div>
      </div>
  </xsl:template>

</xsl:stylesheet>