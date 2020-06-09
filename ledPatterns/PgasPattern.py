###########################################################################################################
# SUBMIT YOUR OWN CUSTOM PATTERN AND SHARE WITH THE WORLD YOUR LED ANIMATIONS!
# Visit https://github.com/project-alice-assistant/HermesLedControl/issues/new?template=custom-pattern-proposal.md
# for more informations
#
# Check models/LedPattern.py for the available functions
# Do NEVER have a function call a super class function directly!!
# It could cause a deadlock! Instead, call self._controller.THE_METHOD_YOU_WANT
#
# @author: Psychokiller1888
# @weblink: https://projectalice.io
# @email: laurentchervet@bluewin.ch
#
###########################################################################################################
import time

from models.LedPattern import LedPattern

class PgasPattern(LedPattern):

	def __init__(self, controller):
		super().__init__(controller)
		self._dnd = False
		self._me = self._controller._mainClass._me

	def showcase(self):
		self.off()

		# self._animator.doubleSidedFilling(color=[255, 255, 255, 255], startAt=start, direction=1, speed=50)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[0, 0, 255, 255], startAt=start, direction=-1, speed=50, new=False)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[0, 255, 0, 255], startAt=start, direction=1, speed=50, new=False)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[255, 0, 255, 255], startAt=start, direction=-1, speed=50, new=False)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[255, 0, 0, 255], startAt=start, direction=1, speed=50, new=False)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[0, 255, 255, 255], startAt=start, direction=-1, speed=50, new=False)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[255, 127, 0, 255], startAt=start, direction=1, speed=50, new=False)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[255, 255, 255, 255], startAt=start, direction=-1, speed=50, new=False)
		# time.sleep(0.1)
		# self._animator.doubleSidedFilling(color=[0, 0, 0, 0], startAt=start, direction=1, speed=50, new=False)

		# time.sleep(6)
		# self._animator.doublePingPong(color=[0, 0, 255, 255], startAt=0, speed=30, duration=5)
		# time.sleep(6)
		# self._animator.blink(color=[255, 0, 0, 2], minBrightness=2, maxBrightness=20, speed=30, smooth=False, repeat=10)
		# time.sleep(6)
		# self._animator.breath(color=[0, 255, 0, 255], minBrightness=2, maxBrightness=25, speed=20, duration=5)
		# time.sleep(6)
		# self._animator.relayRace(color=[255, 0, 0, 255], relayColor=[0, 0, 255, 255], backgroundColor=[0, 255, 0, 255],
		# 						 startAt=0, speed=30, duration=5)
		# time.sleep(6)
		# self._animator.rainbow(brightness=255, speed=30, duration=5)
		# time.sleep(6)
		# self._animator.wheelOverlap(colors=[[255, 255, 0], [0, 255, 0]], brightness=255, speed=30, duration=5)
		# time.sleep(6)
		# self._animator.rotate(color=[0, 0, 255, 255], speed=20, trail=4, duration=5)
		# time.sleep(6)
		# self._animator.waitWheel(color=[0, 0, 255, 255], speed=20, backgroundColor=[255, 0, 0, 255], startAt=0, duration=5)

		# self._animator.windmill(colors=[
		# 	[0, 0, 255, 255],
		# 	[255, 0, 0, 255],
		# 	[0, 255, 0, 255],
		# 	[255, 255, 0, 255],
		# ], smooth=True, speed=50)

		# self.off()

	def wakeupOther(self, siteId):
		if siteId != self._me:
			self.wakeup(siteId=siteId)

	def wakeup(self, siteId):
		color = self._controller.configManager.getSiteAttribute(attribute="color", siteId=siteId, default=[0, 0, 255, 255])

		if len(color) == 3:
			color.append(255)

		self._animator.doublePingPong(color=color, startAt=0, speed=30, duration=2)


	def listen(self, *args):
		self._animator.breath(color=[0, 0, 255, 25], minBrightness=2, maxBrightness=25, speed=20, duration=8)


	def think(self, *args):
		self._animator.rotate(color=[0, 0, 255, 25], speed=20, trail=int(self.numLeds / 3), duration=8)


	def speak(self, *args):
		self._animator.breath(color=[0, 255, 255, 25], minBrightness=2, maxBrightness=25, speed=40, duration=20)


	def idle(self):
		self.off()


	def onError(self, *args):
		self._animator.blink(color=[255, 0, 0, 2], minBrightness=2, maxBrightness=20, speed=300, repeat=3)


	def onSuccess(self, *args):
		pass


	def onStart(self, *args):
		startAnimation = self._controller.configManager.getSiteAttribute(attribute="start_animation", default=True)

		if startAnimation:
			self._animator.rainbow(brightness=255, speed=500, duration=2)



	def onButton1(self, *args):
		pass
