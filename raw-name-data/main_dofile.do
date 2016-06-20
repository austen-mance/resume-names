//clear
//use "A:\bsmf.dta", clear

/////////////////////////////////////////////////////////
//*      Dropping Preliminary Unneeded Variables      *//
/////////////////////////////////////////////////////////
#delimit ;

drop 
 blankv1 
 blankv2
 blankv3
 blankv4
 blankv5
 blankv6
 blankv7
 blankv8
 blankv9
 blankv10
 blankv11
 blankv12
 blankv13
 birthOrder
 birthWeight
 hospitalType
 certType
 solicitation
 gestationLength
 prenatalCare
 lastMenses
 regDate
 liveBirthsDead
 liveBirthsLiving
 terminationEarly
 terminationLate
 totalChildren
 mosLastBirth
 lastBirth
 lastTermDate
 mosLastTerm
 laborComplique
 preggoComplique
 cSection
 birthInjury
 deformedYN
 moProcessed
 birthHour
 hospital
 childDeathDate
 censusTract
 mothersCounty
 mothersAge
 mothersMaidenName
 birthCounty
 birthType
 mothersBirthplace
 fatherAge
 middleName
 censusPlaceCode
 
 birthDate;
#delimit cr

/* Dropping bad data */
drop if nameTruncCode > 0
gen cf = 1 if correctionFlag=="C"
drop if cf == 1


destring motherZIP, replace

gen lastNameMissing=1 if missing(lastName)
gen firstNameMissing=1 if missing(firstName)

drop if lastNameMissing==1
drop if firstNameMissing==1

gen motherZIPMissing=1 if motherZIP==.
drop if motherZIPMissing==1

/* Dropping non-white, non-black people */
drop if race > 20



/*Joining with income datas */
rename motherZIP ZIP
joinby ZIP using "G:\1989income.dta"
rename Medianincome medianIncome



sort firstName race
by firstName: egen nameIncome=mean(medianIncome)
duplicates tag firstName, generate(totalNameCount)
duplicates tag firstName race, generate(nameCountByRace)
//Stata is zero-indexed, so this corresponds to 4 people

generate fracWhite = 2
replace fracWhite = nameCountByRace/totalNameCount if race==10
replace fracWhite = (totalNameCount - nameCountByRace)/totalNameCount if race==20


drop if nameCountByRace < 3

/////////////////////////////////////////////////////////
//*                   Cleaning Up                     *//
/////////////////////////////////////////////////////////
#delimit ;
drop 
 nameCountByRace
 motherZIPMissing
 firstNameMissing
 lastNameMissing
 nameTruncCode 
 cf 
 correctionFlag
 
 lastName
 race
 sex
 motherFirstName
 stateOfRes
 mothersRace
 fatherRace
 fatherHispanic
 motherHispanic
 ZIP
 medianIncome;
#delimit cr

/////////////////////////////////////////////////////////
//*  Condensing everything down to our final dataset  *//
/////////////////////////////////////////////////////////

by firstName: gen dup = cond(_N==1,0,_n)
drop if dup>1
drop dup



tab firstName if fracWhite < 0.4 & nameIncome>37000
