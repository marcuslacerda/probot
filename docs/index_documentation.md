people
	- public
		doc (id=login) = {
	       'login'
	       'name'
	       'phone'
	       'cell'
	       'role'
	       'coach'
	       'manager'
	       'city'
	       'contract'
	       'loaded': datetime.now()
			}
	- pdm
		- doc (id=login) = {
			{people:basic},
			Admission Date
			Admission Years
			Current Proficiency
			Current Proficiency Sigla
			Role Key Position
			Engagement Level by Coach
			Engagement Level by Coachee
			Future Role
			Future Proficiency
			Target Date
			Business Partner			
		}

techgallery
	- skill
		doc (id=generated) = {
			tecnologia, 
			login, 
			skill, 
			endorsements,
			role,
			tower,  (??)
			city, (??)
			contract, (??)
			}
	- spdex
		doc (id=generated) = {
			projeto-flow,
			tecnologia,
			tecnologia_peso,
			login,
			skill,
			endorsements
		}


project
    - setting
		doc (id=flow) {
			tower,
			contract,
			flow,
			knowledge_map, # spreadsheet id 
			team =>  [array login],
			stack => [array technologyname]
		}    
	- metric
		doc (id=contract_flow) {
			tower,
			contract,
			flow,
			event_date
			metric  (pml, spdex, ???)
		}