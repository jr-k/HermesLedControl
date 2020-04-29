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


	def new(self, image=None):
		self._controller.clearLeds()
		if image is not None:
			self._image = image
		else:
			self._image = [[0, 0, 0, 0] for _ in range(self._numLeds)]


	def rainbow(self, brightness=255, speed=100):
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

		self._animationFlag.set()

		while self._animationFlag.isSet():
			for color in rainbowColors:
				for ledX in range(0, self._numLeds):
					self._controller.setLedRGB(ledX, [color[0], color[1], color[2]], brightness)
					time.sleep(1.0 / abs(speed))
					self._controller.show()


	def doubleSidedFilling(self, color, startAt=0, direction=1, speed=10):
		"""
		Fills the strip from both sides
		:param startAt: int
		:param color: array RBGW
		:param direction: 1 or -1
		:param speed: float, in l/s or led per second
		:param startAt: int, the led index where the animation starts
		:return:
		"""
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


	def breath(self, color, minBrightness, maxBrightness, speed=10):
		"""
		Breathes the leds, from min to max brightness
		:param color: array RBGW
		:param speed: float, in l/s or led per second
		:param minBrightness: int
		:param maxBrightness: int
		:return:
		"""

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

			time.sleep(1.0 / abs(speed))


	def rotateImage(self, step):
		"""
		Rotates an image by step number of led
		:param step: int Positive for clockwise, negative for anti clockwise
		"""
		if step == 0:
			self._logger.error('Cannot rotate by 0')
			return

		if step < 0:
			for _ in range(0, step, -1):
				self._image.append(self._image.pop(0))
		else:
			for _ in range(step):
				self._image.insert(0, self._image.pop())
		self._displayImage()


	def rotate(self, color, speed=10, trail=0, startAt=0):
		"""
		Makes a light circulate your strip
		:param color: list, an array containing RGB or RGBW informations
		:param speed: float, in l/s or led per second
		:param trail: int, if greater than 0, leave a trail behind the moving light, with decreased brightness
		:param startAt: int, the led index where the animation starts
		"""

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
			time.sleep(1.0 / abs(speed))
			self.rotateImage(rotationSign)


	def relayRace(self, color, relayColor, backgroundColor=None, speed=10, startAt=0):
		"""
		:param color: array RGBW
		:param relayColor: array RGBW
		:param backgroundColor: array RGBW
		:param speed: float, in l/s or led per second
		:param startAt: int, the led index where the animation starts
		"""
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
				time.sleep(1.0 / abs(speed))
				self._setPixel(relayIndex, backgroundColor)
				relayIndex = self._normalizeIndex(relayIndex + speedIncrement)

				self._setPixel(relayIndex, relayColor)
				self._displayImage()

			self._setPixel(index, backgroundColor)
			index = self._normalizeIndex(index + speedIncrement)


	def doublePingPong(self, color, speed=10, backgroundColor=None, startAt=0):
		"""
		Makes two balls ping pong
		:param color: array RBGW
		:param speed: float, in l/s or led per second
		:param backgroundColor: array RGBW
		:param startAt: int, the led index where the animation starts
		:return:
		"""

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
				time.sleep(1.0 / abs(speed))
				self._setPixel(leftIndex, backgroundColor)
				self._setPixel(rightIndex, backgroundColor)
			while self._animationFlag.isSet() and step >= 0:
				step -= 1
				leftIndex = self._normalizeIndex(index + step)
				rightIndex = self._normalizeIndex(index - step)
				self._setPixel(leftIndex, color)
				self._setPixel(rightIndex, color)
				self._displayImage()
				time.sleep(1.0 / abs(speed))
				self._setPixel(leftIndex, backgroundColor)
				self._setPixel(rightIndex, backgroundColor)


	def waitWheel(self, color, speed=10, backgroundColor=None, startAt=0):
		"""
		Makes two balls ping pong
		:param color: array RBGW
		:param speed: float, in l/s or led per second
		:param backgroundColor: array RGBW
		:param startAt: int, the led index where the animation starts
		:return:
		"""
		if backgroundColor is None:
			backgroundColor = [0, 0, 0, 0]

		self.new()
		self._setPixel(startAt, color)

		index = startAt
		self._animationFlag.set()
		while self._animationFlag.isSet():
			time.sleep(1.0 / abs(speed))
			self._displayImage()
			index += 1
			index = self._normalizeIndex(index)

			if self._image[index] == color:
				self._setPixel(index, backgroundColor)
			else:
				self._setPixel(index, color)


	def blink(self, color, minBrightness, maxBrightness, speed=200, repeat=-1):
		"""
		:param color: array RBGW
		:param minBrightness: int
		:param maxBrightness: int
		:param speed: float, in l/s or led per second
		:param repeat: -1 for infinite or int
		:return:
		"""

		if len(color) > 3:
			color[3] = maxBrightness if color[3] > maxBrightness else color[3]
			color[3] = minBrightness if color[3] < minBrightness else color[3]

		if repeat == -1:
			self.breath(color=color, maxBrightness=maxBrightness, minBrightness=minBrightness, speed=speed)
			return
		
		image = [color]*self._numLeds

		self.new(image)

		for _ in range(repeat):
			bri = self._image[0][3]

			while bri < maxBrightness:
				bri = self._image[0][3]

				for i in range(self._numLeds):
					self._image[i] = color[0], color[1], color[2], bri + 1

				self._displayImage()
				time.sleep(1.0 / abs(speed))

			while bri > minBrightness:
				bri = self._image[0][3]

				for i in range(self._numLeds):
					self._image[i] = color[0], color[1], color[2], bri - 1

				self._displayImage()
				time.sleep(1.0 / abs(speed))


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
