import maya.cmds as cmds
import name
def findRoot(topNode):
	"""
	finds root joints under choosen node
	@param topNode: str, node to search for joints under
	@return: list(str), list of root joints
	"""
	cmds.select(topNode)
	rootJnts = []
	for x in cmds.ls(dag=1, ap=1, sl=1, type="joint"):
		if not cmds.listRelatives( x, p=1, typ="joint"):
			rootJnts.append(x)
	return rootJnts

def extendJointName(topJoint, extention, place='e'):
	"""
	extend name of children of a copied joint
	@param topJoint: str, joint to get listed with its joint hierarchy
	@param extention: str, text that will be added to the prefix
	@param place: str, where to place the extention e= end of suffix, b= beginning of suffix
	"""
	joints = cmds.listRelatives( topJoint, type ='joint', ad=1, f=1)
	names = cmds.listRelatives( topJoint, type ='joint', ad=1, )
	for jnt in range(len(joints)):
		cmds.rename(joints[jnt],name.extendName(extention,names[jnt]))

def shortenJointName(topJoint, extention):
	"""
	delete part of names of joint chain
	@param topJoint: str, joint to get listed with its joint hierarchy
	@param extention: str, text that will be added to the prefix
	"""
	joints = cmds.listRelatives( topJoint, type ='joint', ad=1, f=1)
	names = cmds.listRelatives( topJoint, type ='joint', ad=1, )
	for jnt in range(len(joints)):
		cmds.rename(joints[jnt],names[jnt].replace(extention,'' ))

def jointChain(startJnt, endJnt):
	"""
	creates a list of the joint chain between two joints
	@param startJnt: str, the top joint of the list
	@param endJnt: str, the bottom joint of the list
	@return: str, list of joints between startJnt and endJnt
	"""
	jnt = cmds.ls( endJnt, l=1 )[0].split('|')
	return jnt[jnt.index(startJnt):]