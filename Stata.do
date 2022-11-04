********************************************************************************
********************************************************************************
*This file joints all the data available from the households surveys to computes spending by categories
********************************************************************************
********************************************************************************
*Directories
global r_o "C:\Users\eo\Documents\000_Bases"
global r_d "C:\Users\eo\Documents\003_Market_Trends\001_ENAHO_Representatividad"

*Base procesadas
local bases 603 606d 607 610 612

*Data Years
global per "2012 2013 2014 2015 2016 2017 2018 2019"
********************************************************************************
********************************************************************************

tempfile bd_correl bd_retail


import excel "correl_gastos.xlsx", first clear sheet("categorias")

	save `bd_correl', replace

foreach p of global per{
	
	
	tempfile bd_ingreso bd_jefe_de_hogar
	
	
	*************************************************************************
	*Income database

	u	"C:\Users\eo\Documents\000_Bases\\`p'\\sumaria-`p'.dta", clear

		gen ingreso_pc_mensual = ingmo2hd / (mieperho*12)
		gen gasto_pc_mensual = gashog1d / (mieperho*12)

		keep conglome vivienda hogar ingreso_pc_mensual gasto_pc_mensual factor07
		
		save `bd_ingreso'
		
	*Laboral status

	u	"C:\Users\eo\Documents\000_Bases\\`p'\\enaho01a-`p'-500.dta", clear
		
	
		keep if p203 ==1
		
		rename ocu500 EmpleoJefedeHogar
		rename ocupinf TipodeEmpleoJefedeHogar
		rename p208a EdadJefedeHogar
		
		keep conglome vivienda hogar EmpleoJefedeHogar TipodeEmpleoJefedeHogar EdadJefedeHogar ubigeo
		 
		save `bd_jefe_de_hogar'

	tempfile bd_enaho

	u	"$r_o\\`p'\\enaho01-`p'-601.dta", clear
	
		************************************************************************
		*Food expenditures
		*MODULOS 601
		
		*Data departments
		decode p601b4, gen(Canal)


		collapse (sum) i601c i601b2 (first) p601x, by(conglome vivienda hogar p601a Canal p601d1)
			
		*Spends per category

	drop if substr(p601a,3,2)  == "00"
	
	replace p601a = substr(p601a,1,2) + "00"

	*Average

	gen gasto =  i601c
	gen cantd =  i601b2

	rename p601d1 Frecuencia

	gen modulo = "601"

	rename p601x nom_enaho

	rename p601a cod_enaho
	
	save `bd_enaho', replace

	************************************************************************
	*OTHER EXPENSES
	*MODULOS 600

	foreach mod of local bases{

		display "`mod'"
		
		use	"$r_o\\`p'\\enaho01-`p'-`mod'", clear
		
		local mod_ = substr("`mod'",1,3)
		
		gen modulo = "`mod'"
		gen cod_enaho = p`mod_'n
		
		decode p`mod_'n, gen(nom_enaho)
		
		if "`mod'" ==  "612"{
			
			rename i`mod_'g i`mod_'b
		}
		
		if "`mod'" ==  "606d"{

			rename i`mod_'f i`mod_'b
			rename p`mod_'ee p`mod_'aa
		}
		
		
		gen gasto = i`mod_'b
		
		tostring cod_enaho, replace
		
		
		if "`mod'" == "612"{
			
			gen Canal = "No Especifica"
		
		}
		else{
			
			decode p`mod_'aa, gen(Canal)
			
			tostring Canal, replace
			
		}
		
		collapse (sum) gasto, by(conglome vivienda hogar modulo cod_enaho nom_enaho Canal)	
		
		capture append using `bd_enaho', force
		
		save `bd_enaho', replace


	}
	
	preserve
		tempfile resto
		u "bd_enaho_`p'.dta", clear
			drop if modulo == "601"
			drop if modulo == "603"
			drop if modulo == "606d"
			drop if modulo == "607"
			drop if modulo == "610"
			drop if modulo == "612"
			drop _merge
		save `resto', replace
	restore
	
	append using `resto'
	
	replace Canal = "No Especifica" if Canal == ""
	
	
	

	merge m:1 modulo cod_enaho using `bd_correl'

		drop if _merge == 2
		
		collapse (sum) gasto, by(conglome vivienda hogar GRUPO SUBGRUPO CODIGO_MT Canal )
		
		gen periodo = "`p'"
		
		capture append using `bd_retail', force
		
		save `bd_retail', replace
		
}


gen id_BI_hog = periodo + conglome + vivienda + hogar

export delimited "bd_gastos.csv", replace delimiter(",")