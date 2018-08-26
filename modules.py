import maya.cmds as cmds
import joint
from.import ctrl
import name

def base(characterName, scale=1):

	"""
	@param characterName: str, character name
	@param scale: float, general scale of the rig
	@return None
	"""
	topGrp = cmds.group (n = characterName + 'Rig_grp', em=1)
	rigGrp = cmds.group (n = 'rig_grp', em=1, p= topGrp)
	modelGrp = cmds.group (n = 'model_grp', em=1, p= topGrp)
	ctrl.control(
						prefix = "global", 
						scale = scale * 10, 
						translateTo = " ", 
						rotateTo = " ",
						parent = rigGrp,
						lockChannels = [ "v"],
						shape = 'square',
						direction = 'y',
						)
	#ad a control visibility switch
	cmds.addAttr("global_ctrl", ln = "controlsVisibility", at = 'bool', k=1, dv = 1)
	
	#create a hidden group for joints
	jointsGrp = cmds.group (n = 'jnt_grp', em=1, p= "global_ctrl")
	cmds.setAttr('jnt_grp.v', 0, l=1, k=0)
	
	#create a hidden mod group
	modGrp = cmds.group (n = 'mod_grp', em=1, p= "global_ctrl")
	cmds.setAttr('mod_grp.v',0, l=1, k=0)

	globalModGrp = cmds.group (n = 'modGlobal_grp', em=1, p= "global_ctrl")
	cmds.setAttr('modGlobal_grp.v',0, l=1, k=0)

	#create a control group 
	ctrlGrp = cmds.group (n = 'ctrl_grp', em=1, p= "global_ctrl")
	cmds.connectAttr("global_ctrl.controlsVisibility", "ctrl_grp.v")
	
	#create ik group
	ikGrp = cmds.group (n = 'ik_grp', em=1, p= modGrp)

	#create global assets
	globalCurves = cmds.group(n = 'globalCurves_grp', em=1, p= "rig_grp") 

	#create cluster group
	clusterGrp = cmds.group (n = 'clst_grp', em=1, p= modGrp)


def importModel(characterName, modelFile):
	"""
	imports model and joints
	@param file: str, link to modle file
	@return None
	"""
	cmds.file(modelFile, i = 1, ns='import' )
	cmds.parent( 'import:' + characterName + '_geo', 'model_grp')
	name.removeNamespace('import:' + characterName + '_geo')
	
	#referense model
	cmds.setAttr(characterName + '_geo.overrideEnabled',1)
	cmds.setAttr(characterName + '_geo.overrideDisplayType',2)
	
	#parent skeleton
	for x in joint.findRoot("import:*"):
		cmds.parent(x, 'jnt_grp')
		cmds.listRelatives(x, )
		joint.shortenJointName(x, "import:")
		name.removeNamespace(x)

	#find out what's more in the imported scene
	builderGroup = cmds.ls("import:*_grp", assemblies=1)
	if len(builderGroup) > 1:
		print "WARNING: Excpected only one group from imported asset."
	builderGroup = builderGroup[0]
	builder = cmds.listRelatives(builderGroup)
	
	#puts it in the mod group
	for item in builder:
		cmds.parent(item, "mod_grp")
		name.removeNamespace(item)
	cmds.delete(builderGroup)
	

