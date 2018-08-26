import maya.cmds as cmds
from . import shapes
from . import name
from . import joint


def setColor(curveName):
	cmds.setAttr(curveName + '.ove', 1)
	if curveName.startswith('l_'):
		cmds.setAttr(curveName + '.ovc', 6)
	elif curveName.startswith('r_'):
		cmds.setAttr(curveName + '.ovc', 13)
	else:
		cmds.setAttr(curveName + '.ovc', 22)
def control( 
				prefix = "new", 
				scale = 1.0, 
				translateTo = " ", 
				rotateTo = " ",
				parent = " ",
				pointConstraint = "",
				orientConstraint = "",
				scaleConstraint = "",
				aimConstraint = "",
				poleConstraint = "",
				lockChannels = [ "v","s"],
				shape = 'square',
				direction = 'x'
				):
	"""
	@param prefix: str, prefix to name new objects
	@param scale: float, value for size of control shapes
	@param translateTo: str, reference object for control position
	@param rotateTo: str, reference object for control orientation
	@param parent: str, object to be parent of new control
	@param pointConstraint: str, defines an object to be point constrainted to
	@param orientConstraint: str, defines an object to be orientat constrainted to
	@param scaleConstraint: str, defines an object to be scal constrainted to
	@param aimConstraint: str, defines an object to be aim constrainted to
	@param poleConstraint: str, defines an object to be pole constrainted to
	@param lockChannels: list(str), list of channels on control to be locked and non keyable
	@param shape = 'square',
	@param direction: str, x, y, or z defines direction of the contol
	@return: main control name
	"""
	#scale control
	def shapeScale(shape,offset=False):
		coordinates = []
		for dot in shapes.ctrlShapes[shape]:
			l = []
			for s in dot:
				if offset:
					l.append(s * scale * 1.2)
				else:
					l.append(s * scale)
			coordinates.append(l)
		return coordinates
	#create control and offset
	ctrlObject = cmds.curve( d=1, ep=shapeScale(shape), n= prefix + "_ctrl",) 
	ctrlOffs = cmds.curve( d=1, ep=shapeScale(shape,True), n= prefix + "Offs_ctrl",)
	if direction == 'y'.lower():
		cmds.setAttr(ctrlObject + '.rx', 90)
		cmds.setAttr(ctrlOffs + '.rx', 90)
		cmds.makeIdentity(ctrlObject,a=1, r=1)
		cmds.makeIdentity(ctrlOffs,a=1, r=1)
	elif direction == 'z'.lower():
		cmds.setAttr(ctrlObject + '.ry', 90)
		cmds.setAttr(ctrlOffs + '.rx', 90)
		cmds.makeIdentity(ctrlObject, a=1, r=1,)
		cmds.makeIdentity(ctrlOffs,a=1, r=1,)
	ctrlObjShape = cmds.listRelatives( ctrlObject, s = 1 )[0]
	ctrlOffsShape = cmds.listRelatives( ctrlOffs, s = 1 )[0]
	cmds.rename(ctrlObjShape, prefix + "Ctrl_shape")
	cmds.rename(ctrlOffsShape, prefix + "OffsCtrl_shape")
	ctrlObjShape = cmds.listRelatives( ctrlObject, s = 1 )[0]
	ctrlOffsShape = cmds.listRelatives( ctrlOffs, s = 1 )[0]
	
	#create control group
	ctrlGrp = cmds.group( n= prefix + "Ctrl_grp", em = 1)
	cmds.parent(ctrlOffs, ctrlGrp, )
	cmds.parent(ctrlObject, ctrlOffs, )
	
	#set control color
	setColor(ctrlObjShape)
	setColor(ctrlOffsShape)
	#translate control
	if cmds.objExists( translateTo ):
		cmds.delete( cmds.pointConstraint( translateTo, ctrlGrp ) )
		
	#rotate control
	if cmds.objExists( rotateTo ):
		cmds.delete( cmds.orientConstraint( rotateTo, ctrlGrp ) )

	#parent control
	if cmds.objExists( parent ):
		cmds.parent(ctrlGrp, parent )
		
	# constrain control
	if pointConstraint == orientConstraint:
		if pointConstraint: 
			cmds.parentConstraint( prefix +"_ctrl",pointConstraint ,n= prefix + "_parentCnst")
	elif pointConstraint:
		cmds.pointConstraint( prefix +"_ctrl",pointConstraint ,n= prefix + "_pointCnst")
	elif orientConstraint:
		cmds.orientConstraint( prefix +"_ctrl",orientConstraint ,n= prefix + "_orientCnst")
	if scaleConstraint:
		cmds.scaleConstraint( prefix +"_ctrl",scaleConstraint ,n= prefix + "_scaleCnst")
	if aimConstraint:
		cmds.aimConstraint( prefix +"_ctrl", aimConstraint ,n= prefix + "_aimCnst")
	if poleConstraint:
		cmds.poleVectorConstraint( prefix +"_ctrl", poleConstraint ,n= prefix + "_poleCnst")
		
	#lock control channels	
	singleAttrLockList = []
	
	for lockChannel in lockChannels:
		if lockChannel in [ "t", "r","s",]:
			for axis in ['x','y','z']:
				at = lockChannel + axis
				singleAttrLockList.append(at)
		else:
			singleAttrLockList.append(lockChannel)
	for at in singleAttrLockList:
		cmds.setAttr( ctrlObject + "." + at, l=1, k=0)
		cmds.setAttr( ctrlOffs + "." + at, l=1, k=0)
		
	for attr in [ "t", "r","s",]:
		for axis in ['x','y','z']:
			cmds.setAttr( ctrlGrp + "." + attr+ axis, l=1, k=0)
	if "v" in lockChannels:
		cmds.setAttr( ctrlGrp + "." + "v", l=1, k=0)
		
	#offset visibility control
	cmds.addAttr (ctrlObject, ln="Offset", at="bool",k=1)
	cmds.connectAttr(ctrlObject + ".Offset", ctrlOffsShape + ".v")
	return prefix + "_ctrl"
def jawControl(

			jnt = "jaw_jnt",
			rMax = [0.0,0.0,0.0],
			rMin = [0.0,0.0,0.0],
			tMax = 0,
			tMin = 0,
			locationOffs = (0,0,0),
			sceneScale = 1,
			prefix = "jaw",
			parent = "ctrl_grp"
			):

	"""
	@param jnt: str, joint that should be effected
	@param rMax: [float, float,float], rotation values for open mouth
	@param rMin: [float, float, float], rotation values for closed mout
	@param tMax: [float, float, float], translation values for open mouth
	@param tMin: [float, float, float], translation values for closed mouth
	@param locationOffs: [float, float, float], location of the control relative to joint
	@param scenescale: float, scenescale
	@param prefix: str, name of control
	@param parent: parent for control
	@return: None
	"""
			
	#set current joint position as standard if nothing else is set
	if not tMax:
		tMax = cmds.getAttr(jnt + ".t")[0]
	if not tMin:
		tMin = cmds.getAttr(jnt + ".t")[0]
	if not rMax:
		rMax = cmds.getAttr(jnt + ".r")[0]
	if not rMin:
		rMin = cmds.getAttr(jnt + ".r")[0]

	#import shapes in correct size
	def shapeScale(shape):
		coordinates = []
		for dot in shape:
			l = []
			for s in dot:
				l.append(s * sceneScale)
			coordinates.append(l)
		return coordinates
		
	#creates a jaw group
	group = cmds.group(n= prefix + "ctrl_grp", em = 1)

	#creates the frame		
	frame = cmds.curve( d=1, ep= shapeScale(shapes.jawFrame), n= prefix + "CtrlFrame_crv", )
	cmds.rename(cmds.listRelatives(frame, s = 1 )[0],prefix + "CtrlFrame_shape")
	cmds.setAttr(frame +".ove",1)
	cmds.setAttr(frame +".overrideDisplayType",2)
	
	#creates the lever
	lever = cmds.curve( d=1, ep= shapeScale(shapes.jawLever), n= prefix + "CtrlLever_crv",)
	cmds.rename(cmds.listRelatives(lever, s = 1 )[0],prefix + "CtrlLever_shape")
	cmds.setAttr(lever + '.ove', 1)
	cmds.setAttr(lever + '.ovc', 22)
	cmds.transformLimits(lever, tx=(0, 0), ty=(-0.45*sceneScale, 0.45*sceneScale), tz=(0, 0), etx=(1,1),ety=(1,1),etz=(1,1) )
	
	#connect control to jaw
	rNode = cmds.shadingNode("setRange", asUtility=1 , n = name.removeSuffix(jnt) + "RCtrl_range")
	tNode = cmds.shadingNode("setRange", asUtility=1 , n = name.removeSuffix(jnt) + "TCtrl_range")
	cmds.setAttr("jawTCtrl_range.max",tMax[0],tMax[1],tMax[2],)
	cmds.setAttr("jawRCtrl_range.max",rMax[0],rMax[1],rMax[2],)
	cmds.setAttr("jawTCtrl_range.min",tMin[0],tMin[1],tMin[2],)
	cmds.setAttr("jawRCtrl_range.min",rMin[0],rMin[1],rMin[2],)
	cmds.connectAttr(rNode + '.o', jnt + '.r')
	cmds.connectAttr(tNode + '.o', jnt + '.t')
	for node in (rNode,tNode):
			for axis in ('x', 'y', 'z'):
				cmds.setAttr(node + ".om" + axis, 0.45*sceneScale)
				cmds.setAttr(node + ".on" + axis, -0.45*sceneScale)
				cmds.connectAttr(lever + ".ty", node + '.v' + axis)
	cmds.parent(group, parent)
	cmds.parent(frame ,group)
	cmds.parent(lever, group)
	cmds.delete(cmds.pointConstraint(jnt, group))
	cmds.move(locationOffs[0], locationOffs[1], locationOffs[2], group, r=1)
	cmds.move(0,-0.45*sceneScale,0, lever, r=1)
	cmds.parentConstraint(cmds.pickWalk( jnt, direction='up' )[0],group, mo=1)
def FkIk(limb,firstJnt,secondJnt,thirdJnt,scale, root, location=2):
	"""
	creates Fk/Ik controles
	@param limb: str, name of limb
	@param firstJnt: str, root joint
	@param secondJnt: str, middle joint 
	@param thirdJnt: str, end joint
	@param location: float, controls distance from elobw
	@scale: sceneScale
	"""


	
	#creates Fk/Ik switch
	cmds.addAttr('global_ctrl', ln=limb[0].upper() + limb[1:].lower() + "FkIk", at='double',min=0, max=10, dv=0,k=1, )
	#duplicates the joints to one Fk and one Ik version
	for rig in ('Fk','Ik'):	
		cmds.duplicate(firstJnt, n= name.extendName(rig,firstJnt))
		joint.extendJointName(name.extendName(rig,firstJnt), rig)
	#connect Fk, Ik and skinned joints
	for rig in ('Fk','Ik'):	
		for jnt in cmds.listRelatives(name.extendName(rig,thirdJnt)):
			cmds.delete(jnt)
		for jnt in (firstJnt,secondJnt,thirdJnt):
			cmds.parentConstraint(name.extendName(rig,jnt),jnt, n = name.removeSuffix(jnt) +'_parentCnst')
	#ads Fk controls
	for jnt in (firstJnt,secondJnt,thirdJnt):
		#create math nodes for switch		
		reverse = cmds.shadingNode('reverse',asUtility=1, n= name.removeSuffix(jnt) + '_reverse')
		mult = cmds.shadingNode('multiplyDivide',asUtility=1, n= name.removeSuffix(jnt) + '_mult')
		#connects math nodes from switch to constrain weights
		cmds.setAttr(mult +".input2X", 0.1)
		cmds.connectAttr("global_ctrl."+ limb[0].upper() + limb[1:].lower() +"FkIk",mult +".input1.input1X.")
		cmds.connectAttr(mult + ".output.outputX", reverse + ".input.inputX")
		cmds.connectAttr(reverse +".output.outputX", name.removeSuffix(jnt) +"_parentCnst" + '.' + cmds.listAttr(name.removeSuffix(jnt) +"_parentCnst", r=1, st= name.removeSuffix(jnt)+ "Fk*")[0])
		cmds.connectAttr(mult +".output.outputX",name.removeSuffix(jnt) + "_parentCnst" + '.' + cmds.listAttr(name.removeSuffix(jnt) + "_parentCnst", r=1, st= name.removeSuffix(jnt)+ "Ik*")[0])
	#creates an Fk chain 	
	control(
				prefix = name.removeSuffix(firstJnt) + "Fk", 
				scale = scale, 
				translateTo = name.extendName("Fk",firstJnt), 
				rotateTo = name.extendName("Fk",firstJnt),
				parent = root,
				lockChannels = ["t","s"],
				shape = 'sphere',
				orientConstraint = name.extendName("Fk",firstJnt)
				)
	control(
				prefix = name.removeSuffix(secondJnt) + "Fk", 
				scale = scale*0.75, 
				translateTo = name.extendName("Fk",secondJnt), 
				rotateTo = name.extendName("Fk",secondJnt),
				parent = name.removeSuffix(firstJnt) + "Fk_ctrl",
				lockChannels = [ "v","t","s"],
				shape = 'sphere',
				orientConstraint = name.extendName("Fk",secondJnt)
				)
	control(
				prefix = name.removeSuffix(thirdJnt) + "Fk", 
				scale = scale * 0.5, 
				translateTo = name.extendName("Fk",thirdJnt), 
				rotateTo = name.extendName("Fk",thirdJnt),
				parent = name.removeSuffix(secondJnt) + "Fk_ctrl",
				lockChannels = [ "v","t","s"],
				shape = 'sphere',
				orientConstraint = name.extendName("Fk",thirdJnt)
				)
	
	#turns of Fk visibility in Ik mode	
	cmds.connectAttr(name.removeSuffix(firstJnt) + '_reverse.output.outputX',name.removeSuffix(firstJnt) + "Fk_ctrl.v")

	#creates Ik handle
	ik = cmds.ikHandle(sj=name.extendName("Ik",firstJnt), ee= name.extendName("Ik",thirdJnt), n= limb + "_ik")
	cmds.rename(ik[1], limb + "Ik_eff")
	cmds.parent(ik[0], "ik_grp")
	#create Ik control
	control(
				prefix = name.removeSuffix(thirdJnt) + "Ik", 
				scale = scale*0.75, 
				translateTo = name.extendName("Ik",thirdJnt), 
				rotateTo = name.extendName("Ik",thirdJnt),
				parent = root,
				lockChannels = [ "s"],
				shape = 'box',
				orientConstraint = name.extendName("Ik",thirdJnt),
				pointConstraint = ik[0]
				)
	
	#create control placeholder
	loc = cmds.spaceLocator()[0]
	grp = cmds.group(em=1, n= 'placeholderGrp')
	cmds.parent(loc, grp)
	cmds.delete(cmds.parentConstraint(secondJnt, grp))
	cmds.setAttr(loc + '.tx', location)
	rotation = (180 + cmds.getAttr(secondJnt + '.joy'))/2
	cmds.xform( grp, r=1, ro=(0, -rotation, 0), os =1)
	elbowCtrl = control(
				prefix = name.removeSuffix(secondJnt) + "aimIk", 
				scale = scale * 0.25, 
				translateTo = loc, 
				rotateTo = loc,
				parent = root,
				lockChannels = [ "r","s"],
				shape = 'sphere',
				poleConstraint = ik[0],
				)
	cmds.delete(grp)
	line =cmds.curve( d=1, ep=((0,0,0),(1,0,0)), n= limb + "_crv",)
	

	cmds.parent(limb + "_crv", 'globalCurves_grp')
	setColor(line)
	jntCluster = cmds.cluster(line + '.cv[0]', n= limb + 'ikJntLine_clst',)[1]
	cmds.parent(jntCluster, 'clst_grp')
	ctrlCluster = cmds.cluster(line + '.cv[1]', n= limb + 'ikCtrlLine_clst',)[1]
	cmds.parent(ctrlCluster, 'clst_grp')
	cmds.pointConstraint( elbowCtrl, ctrlCluster, n=limb + 'ikCtrlLineClst_pointCnst')
	cmds.pointConstraint( name.extendName('Ik',secondJnt), jntCluster, n=limb + 'ikJntLineClst_pointCnst')
	cmds.rename(ctrlCluster, limb + 'ikCtrlLineClst_handle') 
	cmds.rename(jntCluster, limb + 'ikJntLineClst_handle') 

	#hide Ik control in Fk mode
	cmds.connectAttr(mult +".output.outputX", name.removeSuffix(thirdJnt) + "Ik_ctrl.v")
	cmds.connectAttr(mult +".output.outputX", name.removeSuffix(secondJnt) + "aimIk_ctrl.v")
	cmds.connectAttr(mult +".output.outputX", limb + "_crv.v")

def tailCtrl(startJnt, endJnt, parent, ctrlNumber, prefix, scale):
	joints = joint.jointChain(startJnt, endJnt)
	coordinates = []
	for jnt in joints:
		loc = cmds.spaceLocator()[0]
		cmds.delete(cmds.parentConstraint(jnt, loc))
		coordinates.append(cmds.getAttr(loc + '.t')[0])
		cmds.delete(loc)
	curve = cmds.curve( d=1, ep=coordinates, n= prefix + "_crv",)
	curve2 = cmds.rebuildCurve(curve, ch=1, rpo=1 ,end=1, kr=0, kt=0, s=ctrlNumber-1)
	count = 1
	ik = cmds.ikHandle(sol= 'ikSplineSolver', roc=0, c= curve, sj=startJnt , ee=endJnt, ccv=0, n=prefix + '_ik')
	
	cmds.parent(ik[0], 'ik_grp')
	#cmds.rename(ik[0], prefix + '_ik')
	cmds.rename(ik[1], prefix + 'ik_eff')
	for point in cmds.ls(curve + '.cv[:]',fl=1)[1:-1]:
		cluster = cmds.cluster(point, n= prefix + str(count).zfill(3) + '_clst')
		cluster = cmds.rename(cluster[1],prefix + str(count).zfill(3)  +'Clst_handle')
		cmds.parent(cluster,'clst_grp')
		if count == 1:
			control(
				prefix = prefix + str(count).zfill(3), 
				scale = scale, 
				translateTo = cluster, 
				rotateTo = cluster,
				parent = parent,
				lockChannels = ["t","s"],
				shape = 'circle',
				pointConstraint = cluster,
				orientConstraint = cluster,
				)
		else:
			control(
				prefix = prefix + str(count).zfill(3), 
				scale = scale, 
				translateTo = cluster, 
				rotateTo = cluster,
				parent = prefix + str(count-1).zfill(3) + '_ctrl',
				lockChannels = ["t","s"],
				shape = 'circle',
				pointConstraint = cluster,
				orientConstraint = cluster,
				)
		count +=1
	cluster = cmds.cluster(cmds.ls(curve + '.cv[:]',fl=1)[-1], n= prefix + str(count).zfill(3) + '_clst')
	cluster = cmds.rename(cluster[1],prefix + str(count).zfill(3)  +'Clst_handle')
	cmds.parent(cluster, prefix + str(count-1).zfill(3)  +'Clst_handle')
