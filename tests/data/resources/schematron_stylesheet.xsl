<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:iso="http://purl.oclc.org/dsdl/schematron" xmlns:svrl="http://purl.oclc.org/dsdl/svrl" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:sch="http://www.ascc.ne/xml/schematron" xmlns:xs="http://www.w3.org/2001/XMLSchema" version="2.0">
    <xsl:output encoding="UTF-8" method="xhtml" indent="yes"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>Schematron Report</title>
				<!--link rel="stylesheet" href="style.css"/-->
				<style>
body
	{
		background-color: #242526;
		font-family: 'Lucida Sans', Arial, sans-serif;
		color: #ffffff;
		width: 80em;
	}

.light-mode
	{
		background-color: #ffffff;
		font-family: 'Lucida Sans', Arial, sans-serif;
		color: #242526;
	}

h1
	{
		/*color: #ffffff; */
		font-family: 'Lato', sans-serif;
		font-size: 40px;
		font-weight: 200;
		line-height: 40px;
	}

h2
	{
		color: #adb7bd;
		font-family: 'Lucida Sans', Arial, sans-serif;
		font-size: 16px;
		line-height: 26px;
	}

p
	{
		font-family: 'Lucida Sans', Arial, sans-serif;
	}

td
	{
		text-align: left;
		padding-left: 10px;
		padding: 5px;
	}

div
	{
		padding-left: 10px;
	}

.inline
	{
		display: inline;
	}

.result-active-pattern
	{
		background-color: #FDCC0D;
		color: #242526;
		padding: 20px 0;
	}

.result-active-pattern-text, .result-assert
	{
		padding: 10px 0 10px 0;
	}

.result-report-text
	{
		font-size: small;
	}

.error-text
	{
		box-shadow: -1px 0 0 1px #fff, 1px 0 0 1px #fff;
		background-color: #990000;
		color: #ffffff;
		padding: 5px;
	}

.result-assert-text
	{
		margin: 10px 0 10px; 0;
	}

/*button*/
.wrapper{
	position: fixed;
	float: right;
	right: 30px;
	top: 5px;
	/* transform: translate(-10%, -100%); */
}

.link_wrapper{
	position: relative;
}

a{
	font-size: 8px;
	display: block;
	width: 125px;
	height: 25px;
	line-height: 25px;
	font-weight: bold;
	text-decoration: none;
	background: #333;
	text-align: center;
	color: #fff;
	text-transform: uppercase;
	letter-spacing: 1px;
	border: 3px solid #333;
	transition: all .35s;
}

.icon{
	width: 20px;
	height: 20px;
	border: 3px solid transparent;
	position: absolute;
	transform: rotate(45deg);
	right: 0;
	top: 3;
	z-index: -1;
	transition: all .35s;
}

.icon svg{
	width: 20px;
	position: absolute;
	left: calc(50% - 15px);
	top: 3;
	transform: rotate(-45deg);
	fill: #2ecc71;
	transition: all .35s;
}

a:hover{
	width: 100px;
	border: 3px solid #2ecc71;
	background: transparent;
	color: #2ecc71;
}

a:hover + .icon{
	border: 3px solid #2ecc71;
	right: -25%;
}

.label, .biglabel{
	padding-right: 5px;
}
				</style>
            </head>
            <body>
				<span>
					<h2>Schematron Report</h2>
					<span class="wrapper">
					  <div class="link_wrapper">
						<a href="#" onclick="darkLightToggle()">dark/light</a>
						<div class="icon">
						  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 268.832 268.832">
							<path d="M265.17 125.577l-80-80c-4.88-4.88-12.796-4.88-17.677 0-4.882 4.882-4.882 12.796 0 17.678l58.66 58.66H12.5c-6.903 0-12.5 5.598-12.5 12.5 0 6.903 5.597 12.5 12.5 12.5h213.654l-58.66 58.662c-4.88 4.882-4.88 12.796 0 17.678 2.44 2.44 5.64 3.66 8.84 3.66s6.398-1.22 8.84-3.66l79.997-80c4.883-4.882 4.883-12.796 0-17.678z"/>
						  </svg>
						</div>
					  </div>
					</span>
				</span>
                <hr class="sch"/>
				<div class="schematron">
                    <div class="result">
                        <xsl:apply-templates />
                    </div>
                </div>
				<script>
					function darkLightToggle() {
						var element = document.body;
						element.classList.toggle("light-mode");
					}
				</script>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="svrl:active-pattern">
        <div class="result-active-pattern">
            <div class="result-active-pattern-name">
                <span class="biglabel">
                    <b><xsl:value-of select="@id"/>:</b>
                </span>
                <xsl:value-of select="@name"/>
            </div>
        </div>
		<div class="result-active-pattern-text"><xsl:value-of select="svrl:text"/></div>
    </xsl:template>
	<xsl:template match="svrl:failed-assert">
        <div class="result-assert">
            <div class="result-assert-test">
                <div class="label inline">
                    <b>Test:</b>
                </div>
				<div class="text inline">
					<xsl:value-of select="@test"/>
				</div>
            </div>
            <div class="result-assert-location">
                <div class="label inline">
                    <b>Location:</b>
                </div>
				<div class="text inline">
					<xsl:value-of select="@location"/>
				</div>
            </div>
            <div class="result-assert-text">
                <div class="label inline">
                    <b>Error report:</b>
                </div>
				<div class="error-text inline">
					<xsl:value-of select="svrl:text"/>
				</div>
            </div>
        </div>
    </xsl:template>
    <xsl:template match="svrl:successful-report">
        <div class="result-report">
            <div class="result-report-text">
                <span class="label">
                    <b>Success report:</b>
                </span>
				<xsl:value-of select="svrl:text"/>
            </div>
        </div>
    </xsl:template>
    <xsl:template match="text()" />
</xsl:stylesheet>
