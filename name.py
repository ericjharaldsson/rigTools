import maya.cmds as cmds

def removeSuffix( name ):
 
	"""
	remove suffix from given name string
	@param name: str, given name sting to process
	@return: str, name without suffix
	"""
	edits = name.split('_')
	if len(edits) < 2:
		return name
	suffix = '_' + edits[-1]
	nameNoSuffix = name[:-len( suffix ) ]
	
	return nameNoSuffix


def removeNamespace(name):
	"""
	deletes namespace from node and return it's new name
	@param name: str, name with namespace
	@return: str, new name
	"""
	if ':' in name:
		cmds.rename(name, name.split(':')[1])
		return name.split(':')[1]
	else:
		return name

def extendName(extention,shortName,place='e'):
	"""
	ad extention to suffix
	@param extention str, extention to ad
	@param shortName str, name of object
	@param place: str, where to place the extention e= end of suffix, b= beginning of suffix
	@return str, extended name
	"""
	newName = ''
	nameSplit = shortName.split("_")
	suffix = nameSplit[-1]
	nameSplit.pop()
	nameSplit[-1] += extention
	if place == 'b'.lower():
		for part in nameSplit:
			newName += suffix
			newName += '_'
		newName += part
	else:
		for part in nameSplit:
			newName += part
			newName += '_'
		newName += suffix
	return newName
