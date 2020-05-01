import logging
import math
import time

class Animations:
	def __init__(self, animationFlag, controller):
		self._logger 		= logging.getLogger('HermesLedControl')
		self._animationFlag = animationFlag
		self._controller 	= controller
		self._numLeds 		= self._controller.hardware['numberOfLeds']

		self._image 		= list()
		self.new()


	def sleepOrExit(self, t):
		if not self._animationFlag.isSet():
			return False

		time.sleep(t)

		return self._animationFlag.isSet()


	def new(self, image=None):
		self._controller.clearLeds()
		if image is not None:
			self._image = image
		else:
			self._image = [[0, 0, 0, 0] for _ in range(self._numLeds)]


	def newCardinalImage(self, colors, trail=0, trailAttenuation=0):
		if trailAttenuation > 1:
			trailAttenuation = 1
		elif trailAttenuation < 0:
			trailAttenuation = 0

		maxTrail = 0 if len(colors) == 0 else (self._numLeds - len(colors)) /  len(colors)

		if trail > maxTrail:
			trail = maxTrail
		elif trail < 0:
			trail = 0

		self.new()

		cardinalSteps = int(math.ceil(self._numLeds / len(colors)))
		self._image = []
		j = 0
		t = 0
		trailBri = 0

		for i in range(self._numLeds):
			if i % cardinalSteps == 0:
				self._image.append(colors[j])
				t = trail
				trailBri = colors[j][3] if len(colors[j]) > 3 else 255
				j += 1
			else:
				interColor = [0, 0, 0, 0]

				if t > 0:
					interColor = colors[j-1] if len(colors[j-1]) > 3 else colors[j-1] + [255]
					trailBri *= trailAttenuation
					interColor[3] = int(trailBri)
					t -= 1

				self._image.append(interColor)


	def windmill(self, colors, speed=20, smooth=True, trail=0, trailAttenuation=1, duration=0):
		if duration:
			return self._controller.putStickyPattern(
				pattern=self.windmill,
				duration=duration,
				colors=colors,
				trail=trail,
				trailAttenuation=trailAttenuation,
				speed=speed
			)

		self.newCardinalImage(colors, trail, trailAttenuation)
		degreesPerLed = 360 / (self._numLeds if smooth else len(colors))
		self._animationFlag.set()

		while self._animationFlag.isSet():
			self.rotateImageByAngle(degreesPerLed)
			time.sleep(1 / abs(speed))


	def wheelOverlap(self, colors, brightness=255, speed=100, duration=0):
		if duration:
			return self._controller.putStickyPattern(
				pattern=self.wheelOverlap,
				duration=duration,
				colors=colors,
				brightness=brightness,
				speed=speed
			)

		self._animationFlag.set()

		while self._animationFlag.isSet():
			for color in colors:
				for ledX in range(0, self._numLeds):
					self._controller.setLedRGB(ledX, [color[0], color[1], color[2]], brightness)
					if not self.sleepOrExit(1.0 / abs(speed)): return
					self._controller.show()


	def rainbow(self, brightness=255, speed=100, duration=0):
		if duration:
			return self._controller.putStickyPattern(
				pattern=self.rainbow,
				duration=duration,
				brightness=brightness,
				speed=speed
			)

		rainbowColors = [
			[255, 0, 0], 	# RED
			[255, 127, 0], 	# ORANGE
			[255, 255, 0],	# YELLOW
			[0, 255, 0], 	# GREEN
			[0, 255, 127], 	# LIME
			[0, 255, 255],	# CYAN
			[0, 0, 255],	# BLUE
			[127, 0, 255],	# PURPLE
			[255, 0, 255], 	# PINK
			[255, 0, 127],	# FUCHSIA
		]

		self.wheelOverlap(colors=rainbowColors, brightness=brightness, speed=speed)


	def doubleSidedFilling(self, color, startAt=0, direction=1, speed=10, new=True, duration=0):
		"""
		Fills the strip from both sides
		:param startAt: int
		:param color: array RBGW
		:param direction: 1 or -1
		:param speed: float, in l/s or led per second
		:param startAt: int, the led index where the animation starts
		:return:
		"""
		if duration:
			return self._controller.putStickyPattern(
				pattern=self.doubleSidedFilling,
				duration=duration,
				color=color,
				startAt=startAt,
				direction=direction,
				speed=speed,
				new=new
			)

		if new:
			self.new()

		r = range(int(round(self._numLeds / 2)) + 1)
		if direction <= 0:
			r = reversed(r)

		index = startAt
		oppositeLed = self._oppositeLed(startAt)
		for i in r:
			positive = self._normalizeIndex(index + i)
			negative = self._normalizeIndex(index - i)

			if positive == startAt or positive == oppositeLed:
				self._controller.setLedRGB(positive, [color[0], color[1], color[2]], color[3])
			else:
				self._controller.setLedRGB(positive, [color[0], color[1], color[2]], color[3])
				self._controller.setLedRGB(negative, [color[0], color[1], color[2]], color[3])

			self._controller.show()
			time.sleep(1.0 / abs(speed))


	def breath(self, color, minBrightness, maxBrightness, speed=10, duration=0):
		"""
		Breathes the leds, from min to max brightness
		:param color: array RBGW
		:param speed: float, in l/s or led per second
		:param minBrightness: int
		:param maxBrightness: int
		:return:
		"""

		if duration:
			return self._controller.putStickyPattern(
				pattern=self.breath,
				duration=duration,
				color=color,
				minBrightness=minBrightness,
				maxBrightness=maxBrightness,
				speed=speed
			)

		if len(color) > 3:
			color[3] = maxBrightness if color[3] > maxBrightness else color[3]
			color[3] = minBrightness if color[3] < minBrightness else color[3]

		image = [color for _ in range(self._numLeds)]

		self.new(image)

		direction = 1
		self._animationFlag.set()
		while self._animationFlag.isSet():
			bri = self._image[0][3]

			if bri >= maxBrightness:
				direction = -1
			elif bri <= minBrightness:
				direction = 1

			for i in range(self._numLeds):
				self._image[i] = color[0], color[1], color[2], bri + direction

			self._displayImage()

			if not self.sleepOrExit(1.0 / abs(speed)): return


	def rotateImage(self, step, preventDisplay=False):
		"""
		Rotates an image by step number of led
		:param step: int Positive for clockwise, negative for anti clockwise
		"""
		if step == 0:
			self._logger.error('Cannot rotate by 0')
			return

		step = int(step)

		if step < 0:
			for _ in range(0, step, -1):
				self._image.append(self._image.pop(0))
		else:
			for _ in range(step):
				self._image.insert(0, self._image.pop())

		if not preventDisplay:
			self._displayImage()


	def rotateImageByAngle(self, angle, preventDisplay=False):
		angle = round(angle)

		if angle == 0:
			self._logger.error('Cannot rotate by {}'.format(angle))
			return

		degreesPerLed = 360 / self._numLeds
		steps = int(math.ceil(angle / degreesPerLed))

		if steps < 0:
			for _ in range(0, steps, -1):
				insertBack = self._image.pop(0)
				self._image.insert(len(self._image), insertBack)
		else:
			for _ in range(steps):
				insertBack = self._image.pop()
				self._image.insert(0, insertBack)

		if not preventDisplay:
			self._displayImage()



	def rotate(self, color, speed=10, trail=0, startAt=0, duration=0):
		"""
		Makes a light circulate your strip
		:param color: list, an array containing RGB or RGBW informations
		:param speed: float, in l/s or led per second
		:param trail: int, if greater than 0, leave a trail behind the moving light, with decreased brightness
		:param startAt: int, the led index where the animation starts
		"""

		if duration:
			return self._controller.putStickyPattern(
				pattern=self.rotate,
				duration=duration,
				color=color,
				trail=trail,
				startAt=startAt,
				speed=speed
			)

		if trail > self._numLeds or trail < 0:
			self._logger.error("Trail can't be longer than amount of leds")
			return

		if startAt > self._numLeds - 1:
			self._logger.error("Cannot start at index {}, max index is {}".format(startAt, self._numLeds - 1))
			return

		self.new()

		# Create an image
		index = startAt
		self._setPixel(index, color)
		rotationSign = 1 if speed >=0 else -1
		if trail > 0:
			fullBrightness = self._controller.defaultBrightness if len(color) < 4 else color[3]
			for i in range(1, trail + 1):
				trailIndex = self._normalizeIndex(index - i * rotationSign)
				color[3] = int(math.ceil(float(fullBrightness / (i + 1))))
				self._setPixel(trailIndex, color)

		self._displayImage()

		self._animationFlag.set()
		while self._animationFlag.isSet():
			if not self.sleepOrExit(1.0 / abs(speed)): return
			self.rotateImage(rotationSign)


	def relayRace(self, color, relayColor, backgroundColor=None, speed=10, startAt=0, duration=0):
		"""
		:param color: array RGBW
		:param relayColor: array RGBW
		:param backgroundColor: array RGBW
		:param speed: float, in l/s or led per second
		:param startAt: int, the led index where the animation starts
		"""

		if duration:
			return self._controller.putStickyPattern(
				pattern=self.relayRace,
				duration=duration,
				color=color,
				relayColor=relayColor,
				backgroundColor=backgroundColor,
				startAt=startAt,
				speed=speed
			)

		if backgroundColor is None:
			backgroundColor = [0, 0, 0, 0]

		self.new()
		for i in range(self._numLeds):
			self._setPixel(i, backgroundColor)

		index = startAt
		self._animationFlag.set()

		speedIncrement = 1 if speed >=0 else -1
		while self._animationFlag.isSet():
			self._setPixel(index, color)
			relayIndex = self._normalizeIndex(index + speedIncrement)

			self._setPixel(relayIndex, relayColor)
			self._displayImage()
			while self._animationFlag.isSet() and relayIndex != index:
				if not self.sleepOrExit(1.0 / abs(speed)): return
				self._setPixel(relayIndex, backgroundColor)
				relayIndex = self._normalizeIndex(relayIndex + speedIncrement)

				self._setPixel(relayIndex, relayColor)
				self._displayImage()

			self._setPixel(index, backgroundColor)
			index = self._normalizeIndex(index + speedIncrement)


	def doublePingPong(self, color, speed=10, backgroundColor=None, startAt=0, duration=0):
		"""
		Makes two balls ping pong
		:param color: array RBGW
		:param speed: float, in l/s or led per second
		:param backgroundColor: array RGBW
		:param startAt: int, the led index where the animation starts
		:return:
		"""

		if duration:
			return self._controller.putStickyPattern(
				pattern=self.doublePingPong,
				duration=duration,
				color=color,
				backgroundColor=backgroundColor,
				startAt=startAt,
				speed=speed
			)

		self.new()

		if backgroundColor is None:
			backgroundColor = [0, 0, 0, 0]
		else:
			for i in range(self._numLeds):
				self._setPixel(i, backgroundColor)

		self._setPixel(startAt, color)

		index = startAt
		self._animationFlag.set()
		while self._animationFlag.isSet():
			self._displayImage()
			step = 0
			while self._animationFlag.isSet() and step != round(self._numLeds / 2):
				step += 1
				leftIndex = self._normalizeIndex(index - step)
				rightIndex = self._normalizeIndex(index + step)
				self._setPixel(leftIndex, color)
				self._setPixel(rightIndex, color)
				self._displayImage()
				if not self.sleepOrExit(1.0 / abs(speed)): return
				self._setPixel(leftIndex, backgroundColor)
				self._setPixel(rightIndex, backgroundColor)
			while self._animationFlag.isSet() and step >= 0:
				step -= 1
				leftIndex = self._normalizeIndex(index + step)
				rightIndex = self._normalizeIndex(index - step)
				self._setPixel(leftIndex, color)
				self._setPixel(rightIndex, color)
				self._displayImage()
				if not self.sleepOrExit(1.0 / abs(speed)): return
				self._setPixel(leftIndex, backgroundColor)
				self._setPixel(rightIndex, backgroundColor)


	def waitWheel(self, color, speed=10, backgroundColor=None, startAt=0, duration=0):
		"""
		Makes two balls ping pong
		:param color: array RBGW
		:param speed: float, in l/s or led per second
		:param backgroundColor: array RGBW
		:param startAt: int, the led index where the animation starts
		:return:
		"""

		if duration:
			return self._controller.putStickyPattern(
				pattern=self.waitWheel,
				duration=duration,
				color=color,
				backgroundColor=backgroundColor,
				startAt=startAt,
				speed=speed
			)

		if backgroundColor is None:
			backgroundColor = [0, 0, 0, 0]

		self.new()
		self._setPixel(startAt, color)

		index = startAt
		self._animationFlag.set()
		while self._animationFlag.isSet():
			if not self.sleepOrExit(1.0 / abs(speed)): return
			self._displayImage()
			index += 1
			index = self._normalizeIndex(index)

			if self._image[index] == color:
				self._setPixel(index, backgroundColor)
			else:
				self._setPixel(index, color)


	def blink(self, color, minBrightness, maxBrightness, speed=200, repeat=-1, smooth=True, duration=0):
		"""
		:param color: array RBGW
		:param minBrightness: int
		:param maxBrightness: int
		:param speed: float, in l/s or led per second
		:param repeat: -1 for infinite or int
		:return:
		"""
		if duration:
			return self._controller.putStickyPattern(
				pattern=self.blink,
				duration=duration,
				color=color,
				minBrightness=minBrightness,
				maxBrightness=maxBrightness,
				repeat=repeat,
				smooth=smooth,
				speed=speed
			)

		if len(color) > 3:
			color[3] = maxBrightness if color[3] > maxBrightness else color[3]
			color[3] = minBrightness if color[3] < minBrightness else color[3]

		if repeat == -1 and smooth:
			self.breath(color=color, maxBrightness=maxBrightness, minBrightness=minBrightness, speed=speed, duration=duration)
			return
		
		image = [color]*self._numLeds
		self.new(image)
		self._animationFlag.set()
		turn = 0

		while self._animationFlag.isSet() and (turn < repeat or repeat == -1):
			bri = self._image[0][3]

			while self._animationFlag.isSet() and bri < maxBrightness:
				bri = self._image[0][3]

				if not smooth:
					bri = maxBrightness

				for i in range(self._numLeds):
					self._image[i] = color[0], color[1], color[2], bri + 1

				self._displayImage()
				if not self.sleepOrExit(1.0 / abs(speed)): return

			while self._animationFlag.isSet() and bri > minBrightness:
				bri = self._image[0][3]

				if not smooth:
					bri = minBrightness

				for i in range(self._numLeds):
					self._image[i] = color[0], color[1], color[2], bri - 1

				self._displayImage()
				if not self.sleepOrExit(1.0 / abs(speed)): return

			turn +=1

		self.new()

	def _setPixel(self, index, color):
		if index >= len(self._image) or index < 0:
			self._logger.error("Cannot assign led index {}, out of bound".format(index))
			return
		self._image[index] = [color[0], color[1], color[2], color[3]]


	def _displayImage(self):
		for i, led in enumerate(self._image[:self._numLeds]):
			self._controller.setLedRGB(i, led)

		self._controller.show()


	def _normalizeIndex(self, index):
		"""
		Makes sure the given index is valid in the led strip or returns the one on the other side of the loop
		:param int index:
		:return: int
		"""
		if index < 0:
			return self._numLeds - abs(index)
		elif index >= self._numLeds:
			return index - self._numLeds
		else:
			return index


	def _oppositeLed(self, index):
		return self._normalizeIndex(index + int(round(self._numLeds / 2)))
