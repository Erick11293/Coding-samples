import scrapy
import re
import numpy as np
from scrapy.shell import inspect_response
from unidecode import unidecode
from ..items import ConsultaamigableItem

scrapped = []


class ConsultaAmigable(scrapy.Spider):
    name = "consultaamigable"
    #start_urls = ["https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2020&ap=ActProy"]


    start_urls = [
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_2.aspx?y=2005&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_2.aspx?y=2006&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_3.aspx?y=2007&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_3.aspx?y=2008&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_4.aspx?y=2009&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_4.aspx?y=2010&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_4.aspx?y=2011&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_5.aspx?y=2012&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_5.aspx?y=2013&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_5.aspx?y=2014&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_5.aspx?y=2015&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2016&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2017&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2018&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2019&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2020&ap=ActProy",
        # "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2021&ap=ActProy",
        "https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2022&ap=ActProy",
    ]


    #start_urls = ["https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx?y=2021&ap=ActProy"]

    def parse(self, response):

        try:
            hierarchy = response.meta["hierarchy"]
        except:
            hierarchy = []
        try:
            year = response.meta["year"]
        except:
            year = response.url.split("=")[1].split("&")[0]

        __VIEWSTATE = response.xpath('//*[@name="__VIEWSTATE"]/@value').get()
        __EVENTVALIDATION = response.xpath('//*[@name="__EVENTVALIDATION"]/@value').get()
        grp1_list = response.xpath('//*[@name="grp1"]/@value')
        levels_available = response.xpath("//input[@type='submit']/@name").getall()

        order_levels = ['ctl00$CPH1$BtnTipoGobierno',
                        'ctl00$CPH1$BtnFuncion',
                        'ctl00$CPH1$BtnGenerica',
                        'ctl00$CPH1$BtnGrupoGasto',
                        'ctl00$CPH1$BtnDepartamentoMeta',
                        'ctl00$CPH1$BtnSubTipoGobierno',
                        'ctl00$CPH1$BtnDepartamento',
                        'ctl00$CPH1$BtnMancomunidad',
                        'ctl00$CPH1$BtnProvincia'


        ]

        levels_required = [level for level in order_levels if level in levels_available]

        response_hold = response

        if len(levels_required)>0:
            response_required = levels_required[0]

            for grp_element in grp1_list:

                #inspect_response(response, self)
                # response.xpath("//input[@type='submit']"

                response_required_value = response.xpath(f'//*[@name="{response_required}"]/@value').get()
                form = {
                    '__VIEWSTATE': __VIEWSTATE,
                    '__EVENTVALIDATION': __EVENTVALIDATION,
                    'Year': year,
                    'ctl00%24CPH1%24DrpActProy': 'ActProy',
                    response_required: response_required_value,
                    'grp1': grp_element.get()
                }

                req = scrapy.FormRequest.from_response(response_hold,
                                                       formdata=form,
                                                       callback=self.parse,
                                                       meta = {'hierarchy': hierarchy + [grp_element.get(), response_required],
                                                               'year': year
                                                               }
                                                       )

                yield req

        else:
            #print(response.text)
            #inspect_response(response, self)
            levels_consulted = response.xpath("//table[@class='History']/tr/td[2]/text()").getall()
            levels_consulted = [level for level in levels_consulted if ":" in level]

            data_level = response.xpath('//*[@name="grp1"]/@value').getall()

            data = ConsultaamigableItem()
            detalle = {}
            for level in levels_consulted:
                level_1, level_2 = level.split(":")
                level_1 = unidecode(level_1)
                level_1 = "".join(level_1.split(" ")[:-1])
                level_1 = level_1.replace('\r','').replace('\n','')
                level_2 = unidecode(level_2)
                level_2 = level_2.replace(" ", "").replace('\r','').replace('\n','')
                detalle[level_1] = level_2

            data['data'] = data_level
            data['url'] = response.url
            data['detalle'] = detalle
            data['hierarchy'] = hierarchy

            yield data